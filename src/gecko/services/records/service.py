from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import UUID
from zoneinfo import ZoneInfo

from gecko.services.beaver import errors as be
from gecko.services.beaver import models as bm
from gecko.services.beaver.service import BeaverService
from gecko.services.emerald import errors as ee
from gecko.services.emerald import models as em
from gecko.services.emerald.service import EmeraldService
from gecko.services.records import errors as e
from gecko.services.records import models as m


class RecordsService:
    """Service to manage records."""

    def __init__(self, beaver: BeaverService, emerald: EmeraldService):
        self._beaver = beaver
        self._emerald = emerald

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except be.ServiceError as ex:
            raise e.BeaverError(str(ex)) from ex
        except ee.ServiceError as ex:
            raise e.EmeraldError(str(ex)) from ex

    @contextmanager
    def _handle_not_found(self, event: UUID, start: datetime) -> Generator[None]:
        try:
            yield
        except ee.NotFoundError as ex:
            raise e.RecordNotFoundError(event, start) from ex

    async def _get_event(self, event: UUID) -> bm.Event | None:
        req = bm.EventsGetRequest(
            id=event,
            include=None,
        )

        with self._handle_errors():
            try:
                res = await self._beaver.events.mget(req)
            except be.ServiceError as ex:
                if hasattr(ex, "response"):
                    if ex.response.status_code == HTTPStatus.NOT_FOUND:
                        return None

                raise

        ev = res.event

        if ev.type != bm.EventType.live:
            raise e.BadEventTypeError(ev.type)

        return ev

    async def _get_instance(
        self, event: UUID, start: datetime
    ) -> bm.EventInstance | None:
        mevent = await self._get_event(event)

        if mevent is None:
            return None

        tz = ZoneInfo(mevent.timezone)
        utcstart = start.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
        utcstart = utcstart.astimezone(UTC).replace(tzinfo=None)
        utcend = utcstart + timedelta(days=1)

        req = bm.ScheduleListRequest(
            start=utcstart,
            end=utcend,
            limit=None,
            offset=None,
            where={
                "id": str(mevent.id),
            },
            include=None,
            order=None,
        )

        with self._handle_errors():
            res = await self._beaver.schedule.list(req)

        schedules = res.results.schedules

        schedule = next(iter(schedules), None)

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

    async def _list_get_objects(self, prefix: str) -> list[em.Object]:
        req = em.ListRequest(
            prefix=prefix,
            recursive=False,
        )

        with self._handle_errors():
            res = await self._emerald.list(req)
            return [object async for object in res.objects]

    def _list_map_objects(self, objects: list[em.Object]) -> list[m.Record]:
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

        req = em.DownloadRequest(
            name=key,
        )

        with self._handle_errors():
            with self._handle_not_found(event, start):
                res = await self._emerald.download(req)

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

        req = em.UploadRequest(
            name=key,
            content=content,
        )

        with self._handle_errors():
            await self._emerald.upload(req)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a record."""

        event = request.event
        start = request.start

        if await self._get_instance(event, start) is None:
            raise e.InstanceNotFoundError(event, start)

        key = self._make_key(event, start)

        req = em.DeleteRequest(
            name=key,
        )

        with self._handle_errors():
            with self._handle_not_found(event, start):
                await self._emerald.delete(req)

        return m.DeleteResponse()
