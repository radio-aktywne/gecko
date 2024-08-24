from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from emirecords.services.emishows import errors as ee
from emirecords.services.emishows import models as em
from emirecords.services.emishows.service import EmishowsService
from emirecords.services.mediarecords import errors as me
from emirecords.services.mediarecords import models as mm
from emirecords.services.mediarecords.service import MediarecordsService
from emirecords.services.records import errors as e
from emirecords.services.records import models as m


class RecordsService:
    """Service to manage records."""

    def __init__(self, emishows: EmishowsService, mediarecords: MediarecordsService):
        self._emishows = emishows
        self._mediarecords = mediarecords

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ee.ServiceError as ex:
            raise e.EmishowsError(str(ex)) from ex
        except me.ServiceError as ex:
            raise e.MediarecordsError(str(ex)) from ex

    @contextmanager
    def _handle_not_found(self, event: UUID, start: datetime) -> Generator[None]:
        try:
            yield
        except me.NotFoundError as ex:
            raise e.RecordNotFoundError(event, start) from ex

    async def _get_event(self, event: UUID) -> em.Event | None:
        req = em.EventsGetRequest(
            id=event,
            include=None,
        )

        with self._handle_errors():
            try:
                res = await self._emishows.events.mget(req)
            except ee.ServiceError as ex:
                if hasattr(ex, "response"):
                    if ex.response.status_code == HTTPStatus.NOT_FOUND:
                        return None

                raise

        return res.event

    async def _get_instance(
        self, event: UUID, start: datetime
    ) -> em.EventInstance | None:
        req = em.ScheduleListRequest(
            start=start,
            end=start,
            limit=None,
            offset=None,
            where={
                "id": str(event),
            },
            include=None,
            order=None,
        )

        with self._handle_errors():
            res = await self._emishows.schedule.list(req)

        results = res.results
        schedules = results.schedules

        schedule = next(iter(schedules), None)

        if schedule is None:
            return None

        return next(
            (instance for instance in schedule.instances if instance.start == start),
            None,
        )

    def _make_prefix(self, event: UUID) -> str:
        return f"{event}/"

    def _make_name(self, start: datetime) -> str:
        return start.isoformat()

    def _make_key(self, event: UUID, start: datetime) -> str:
        prefix = self._make_prefix(event)
        name = self._make_name(start)
        return f"{prefix}{name}"

    def _parse_prefix(self, prefix: str) -> UUID:
        return UUID(prefix[:-1])

    def _parse_name(self, name: str) -> datetime:
        return datetime.fromisoformat(name)

    def _parse_key(self, key: str) -> tuple[UUID, datetime]:
        split = key.find("/")
        prefix, name = key[: split + 1], key[split + 1 :]
        event = self._parse_prefix(prefix)
        start = self._parse_name(name)
        return event, start

    async def _list_get_objects(self, prefix: str) -> list[mm.Object]:
        req = mm.ListRequest(
            prefix=prefix,
            recursive=False,
        )

        with self._handle_errors():
            res = await self._mediarecords.list(req)
            return [object async for object in res.objects]

    def _list_map_objects(self, objects: list[mm.Object]) -> list[m.Record]:
        records = []

        for object in objects:
            event, start = self._parse_key(object.name)

            record = m.Record(
                event=event,
                start=start,
            )

            records.append(record)

        return records

    def _list_sort_records(
        self, records: list[m.Record], order: m.ListOrder | None
    ) -> list[m.Record]:
        if order is None:
            return records

        return sorted(
            records,
            key=lambda record: record.start,
            reverse=order == m.ListOrder.DESCENDING,
        )

    def _list_filter_records(
        self, records: list[m.Record], after: datetime | None, before: datetime | None
    ) -> list[m.Record]:
        if after is not None:
            records = [record for record in records if record.start > after]

        if before is not None:
            records = [record for record in records if record.start < before]

        return records

    def _list_pick_records(
        self, records: list[m.Record], limit: int | None, offset: int | None
    ) -> list[m.Record]:
        if offset is not None:
            records = records[offset:]

        if limit is not None:
            records = records[:limit]

        return records

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List records."""

        event = request.event
        after = request.after
        before = request.before
        limit = request.limit
        offset = request.offset
        order = request.order

        if await self._get_event(event) is None:
            raise e.EventNotFoundError(event)

        prefix = self._make_prefix(event)

        objects = await self._list_get_objects(prefix)
        records = self._list_map_objects(objects)
        records = self._list_filter_records(records, after, before)
        records = self._list_sort_records(records, order)

        count = len(records)

        records = self._list_pick_records(records, limit, offset)

        return m.ListResponse(
            count=count,
            limit=limit,
            offset=offset,
            records=records,
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a record."""

        event = request.event
        start = request.start

        if await self._get_instance(event, start) is None:
            raise e.InstanceNotFoundError(event, start)

        key = self._make_key(event, start)

        req = mm.DownloadRequest(
            name=key,
        )

        with self._handle_errors():
            with self._handle_not_found(event, start):
                res = await self._mediarecords.download(req)

        content = res.content

        return m.DownloadResponse(
            content=content,
        )

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload a record."""

        event = request.event
        start = request.start
        content = request.content

        if await self._get_instance(event, start) is None:
            raise e.InstanceNotFoundError(event, start)

        key = self._make_key(event, start)

        req = mm.GetRequest(
            name=key,
        )

        with self._handle_errors():
            try:
                await self._mediarecords.get(req)
            except me.NotFoundError:
                pass
            else:
                raise e.RecordAlreadyExistsError(event, start)

        req = mm.UploadRequest(
            name=key,
            content=content,
        )

        with self._handle_errors():
            await self._mediarecords.upload(req)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a record."""

        event = request.event
        start = request.start

        if await self._get_instance(event, start) is None:
            raise e.InstanceNotFoundError(event, start)

        key = self._make_key(event, start)

        req = mm.DeleteRequest(
            name=key,
        )

        with self._handle_errors():
            with self._handle_not_found(event, start):
                await self._mediarecords.delete(req)

        return m.DeleteResponse()
