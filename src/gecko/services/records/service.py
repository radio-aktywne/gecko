from collections.abc import Generator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import UUID

from gecko.services.beaver import errors as be
from gecko.services.beaver import models as bm
from gecko.services.beaver.service import BeaverService
from gecko.services.emerald import errors as ee
from gecko.services.emerald import models as em
from gecko.services.emerald.service import EmeraldService
from gecko.services.records import errors as e
from gecko.services.records import models as m
from gecko.utils.time import isoparse, isostringify


class RecordsService:
    """Service to manage records."""

    def __init__(self, beaver: BeaverService, emerald: EmeraldService) -> None:
        self._beaver = beaver
        self._emerald = emerald

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except be.ServiceError as ex:
            raise e.BeaverError from ex
        except ee.ServiceError as ex:
            raise e.EmeraldError from ex

    @contextmanager
    def _handle_not_found(self, event: UUID, start: datetime) -> Generator[None]:
        try:
            yield
        except ee.NotFoundError as ex:
            raise e.RecordNotFoundError(event, start) from ex

    async def _get_event(self, event: UUID) -> bm.Event | None:
        events_get_request = bm.EventsGetRequest(id=event)

        with self._handle_errors():
            try:
                events_get_response = await self._beaver.events.get_by_id(
                    events_get_request
                )
            except be.ResponseError as ex:
                if ex.response.status_code == HTTPStatus.NOT_FOUND:
                    return None

                raise

        if events_get_response.event.type != bm.EventType.live:
            raise e.BadEventTypeError(events_get_response.event.type)

        return events_get_response.event

    async def _get_instance(
        self, event: UUID, start: datetime
    ) -> bm.EventInstance | None:
        mevent = await self._get_event(event)

        if mevent is None:
            return None

        utcstart = (
            start.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=mevent.timezone
            )
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
        utcend = utcstart + timedelta(days=1)

        schedule_list_request = bm.ScheduleListRequest(
            start=utcstart, end=utcend, where={"id": str(mevent.id)}
        )

        with self._handle_errors():
            schedule_list_response = await self._beaver.schedule.list(
                schedule_list_request
            )

        schedule = next(iter(schedule_list_response.results.schedules), None)

        if schedule is None:
            return None

        if schedule.event.type != bm.EventType.live:
            raise e.BadEventTypeError(schedule.event.type)

        return next(
            (instance for instance in schedule.instances if instance.start == start),
            None,
        )

    def _make_prefix(self, event: UUID) -> str:
        return f"{event}/"

    def _make_name(self, start: datetime) -> str:
        return isostringify(start)

    def _make_key(self, event: UUID, start: datetime) -> str:
        prefix = self._make_prefix(event)
        name = self._make_name(start)
        return f"{prefix}{name}"

    def _parse_prefix(self, prefix: str) -> UUID:
        return UUID(prefix[:-1])

    def _parse_name(self, name: str) -> datetime:
        return isoparse(name)

    def _parse_key(self, key: str) -> tuple[UUID, datetime]:
        split = key.find("/")
        prefix, name = key[: split + 1], key[split + 1 :]
        event = self._parse_prefix(prefix)
        start = self._parse_name(name)
        return event, start

    async def _list_get_objects(self, prefix: str) -> Sequence[em.Object]:
        list_request = em.ListRequest(prefix=prefix, recursive=False)

        with self._handle_errors():
            list_response = await self._emerald.list(list_request)
            return [obj async for obj in list_response.objects]

    def _list_map_objects(self, objects: Sequence[em.Object]) -> Sequence[m.Record]:
        records = []

        for obj in objects:
            event, start = self._parse_key(obj.name)
            record = m.Record(event=event, start=start)
            records.append(record)

        return records

    def _list_sort_records(
        self, records: Sequence[m.Record], order: m.ListOrder | None
    ) -> Sequence[m.Record]:
        if order is None:
            return records

        return sorted(
            records,
            key=lambda record: record.start,
            reverse=order == m.ListOrder.DESCENDING,
        )

    def _list_filter_records(
        self,
        records: Sequence[m.Record],
        after: datetime | None,
        before: datetime | None,
    ) -> Sequence[m.Record]:
        if after is not None:
            records = [record for record in records if record.start > after]

        if before is not None:
            records = [record for record in records if record.start < before]

        return records

    def _list_pick_records(
        self,
        records: Sequence[m.Record],
        limit: int | None,
        offset: int | None,
    ) -> Sequence[m.Record]:
        if offset is not None:
            records = records[offset:]

        if limit is not None:
            records = records[:limit]

        return records

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List records."""
        if await self._get_event(request.event) is None:
            raise e.EventNotFoundError(request.event)

        prefix = self._make_prefix(request.event)

        objects = await self._list_get_objects(prefix)
        records = self._list_map_objects(objects)
        records = self._list_filter_records(records, request.after, request.before)
        records = self._list_sort_records(records, request.order)

        count = len(records)

        records = self._list_pick_records(records, request.limit, request.offset)

        return m.ListResponse(
            count=count,
            limit=request.limit,
            offset=request.offset,
            records=records,
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a record."""
        if await self._get_instance(request.event, request.start) is None:
            raise e.InstanceNotFoundError(request.event, request.start)

        key = self._make_key(request.event, request.start)

        download_request = em.DownloadRequest(name=key)

        with (
            self._handle_errors(),
            self._handle_not_found(request.event, request.start),
        ):
            download_response = await self._emerald.download(download_request)

        return m.DownloadResponse(content=download_response.content)

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload a record."""
        if await self._get_instance(request.event, request.start) is None:
            raise e.InstanceNotFoundError(request.event, request.start)

        key = self._make_key(request.event, request.start)

        upload_request = em.UploadRequest(name=key, content=request.content)

        with self._handle_errors():
            await self._emerald.upload(upload_request)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a record."""
        if await self._get_instance(request.event, request.start) is None:
            raise e.InstanceNotFoundError(request.event, request.start)

        key = self._make_key(request.event, request.start)

        delete_request = em.DeleteRequest(name=key)

        with (
            self._handle_errors(),
            self._handle_not_found(request.event, request.start),
        ):
            await self._emerald.delete(delete_request)

        return m.DeleteResponse()
