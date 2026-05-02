import asyncio
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
from gecko.services.recordings import errors as e
from gecko.services.recordings import models as m
from gecko.services.recordings.utils import ContentTypeChecker
from gecko.utils.mime import MimeType, MimeTypeValidationError
from gecko.utils.time import isoparse, isostringify


class RecordingsService:
    """Service to manage recordings."""

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
            raise e.RecordingNotFoundError(event, start) from ex

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

        return events_get_response.event

    async def _get_instances(
        self, event: bm.Event, after: datetime, before: datetime
    ) -> Sequence[bm.EventInstance]:
        utcafter = (
            after.replace(tzinfo=event.timezone).astimezone(UTC).replace(tzinfo=None)
        )
        utcbefore = (
            before.replace(tzinfo=event.timezone).astimezone(UTC).replace(tzinfo=None)
        )

        schedule_list_request = bm.ScheduleListRequest(
            start=utcafter, end=utcbefore, where={"id": str(event.id)}
        )

        with self._handle_errors():
            schedule_list_response = await self._beaver.schedule.list(
                schedule_list_request
            )

        schedule = next(iter(schedule_list_response.results.schedules), None)

        if not schedule:
            return []

        return schedule.instances

    async def _get_instance(
        self, event: bm.Event, start: datetime
    ) -> bm.EventInstance | None:
        after = start.replace(hour=0, minute=0, second=0, microsecond=0)
        before = after + timedelta(days=1)
        instances = await self._get_instances(event, after, before)

        return next(
            (instance for instance in instances if instance.start == start),
            None,
        )

    async def _get_object(self, name: str) -> em.ObjectDetails | None:
        get_request = em.GetRequest(name=name)

        with self._handle_errors():
            try:
                get_response = await self._emerald.get(get_request)
            except ee.NotFoundError:
                return None

        return get_response.object

    def _make_prefix(self, event: UUID) -> str:
        return f"{event}/"

    def _make_name(self, start: datetime) -> str:
        return isostringify(start)

    def _make_key(self, event: UUID, start: datetime) -> str:
        prefix = self._make_prefix(event)
        name = self._make_name(start)
        return f"{prefix}{name}"

    def _parse_prefix(self, prefix: str) -> UUID | None:
        try:
            return UUID(prefix[:-1])
        except ValueError:
            return None

    def _parse_name(self, name: str) -> datetime | None:
        try:
            return isoparse(name)
        except ValueError:
            return None

    def _parse_key(self, key: str) -> tuple[UUID, datetime] | None:
        split = key.find("/")
        prefix, name = key[: split + 1], key[split + 1 :]
        event = self._parse_prefix(prefix)
        start = self._parse_name(name)

        return (event, start) if event and start else None

    def _parse_content_type(self, value: str | None) -> MimeType | None:
        if value is None:
            return None

        try:
            parsed = MimeType.parse(value)
        except MimeTypeValidationError:
            return None

        return parsed if ContentTypeChecker().check(parsed) else None

    async def _list_get_objects(self, prefix: str) -> Sequence[em.ObjectListing]:
        list_request = em.ListRequest(prefix=prefix, recursive=False)

        with self._handle_errors():
            list_response = await self._emerald.list(list_request)
            return [obj async for obj in list_response.objects]

    def _list_map_objects(
        self, objects: Sequence[em.ObjectListing]
    ) -> Sequence[m.Recording]:
        return [
            m.Recording(event=event, start=start)
            for obj in objects
            if (parsed := self._parse_key(obj.name))
            for event, start in [parsed]
        ]

    def _list_filter_recordings_by_time(
        self,
        recordings: Sequence[m.Recording],
        after: datetime | None,
        before: datetime | None,
    ) -> Sequence[m.Recording]:
        return [
            recording
            for recording in recordings
            if (after is None or recording.start >= after)
            and (before is None or recording.start < before)
        ]

    async def _list_filter_recordings_by_instance(
        self, recordings: Sequence[m.Recording], event: bm.Event
    ) -> Sequence[m.Recording]:
        after = min(recording.start for recording in recordings)
        after = after.replace(hour=0, minute=0, second=0, microsecond=0)

        before = max(recording.start for recording in recordings)
        before = before.replace(hour=0, minute=0, second=0, microsecond=0)
        before = before + timedelta(days=1)

        instances = await self._get_instances(event, after, before)
        starts = {instance.start for instance in instances}

        return [recording for recording in recordings if recording.start in starts]

    async def _list_filter_recordings_by_content_type(
        self, recordings: Sequence[m.Recording]
    ) -> Sequence[m.Recording]:
        semaphore = asyncio.Semaphore(10)

        async def get(recording: m.Recording) -> em.ObjectDetails | None:
            key = self._make_key(recording.event, recording.start)

            async with semaphore:
                return await self._get_object(key)

        details = await asyncio.gather(*[get(recording) for recording in recordings])

        return [
            recording
            for recording, detail in zip(recordings, details, strict=False)
            if detail and self._parse_content_type(detail.type)
        ]

    async def _list_filter_recordings(
        self,
        recordings: Sequence[m.Recording],
        event: bm.Event,
        after: datetime | None,
        before: datetime | None,
    ) -> Sequence[m.Recording]:
        recordings = self._list_filter_recordings_by_time(recordings, after, before)

        if not recordings:
            return []

        recordings = await self._list_filter_recordings_by_instance(recordings, event)

        if not recordings:
            return []

        return await self._list_filter_recordings_by_content_type(recordings)

    def _list_sort_recordings(
        self, recordings: Sequence[m.Recording], order: m.ListOrder | None
    ) -> Sequence[m.Recording]:
        if order is None:
            return recordings

        return sorted(
            recordings,
            key=lambda recording: recording.start,
            reverse=order == m.ListOrder.DESCENDING,
        )

    def _list_pick_recordings(
        self,
        recordings: Sequence[m.Recording],
        limit: int | None,
        offset: int | None,
    ) -> Sequence[m.Recording]:
        if offset is not None:
            recordings = recordings[offset:]

        if limit is not None:
            recordings = recordings[:limit]

        return recordings

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List recordings."""
        event = await self._get_event(request.event)

        if not event:
            raise e.EventNotFoundError(request.event)

        if event.type != bm.EventType.live:
            raise e.BadEventTypeError(event.type)

        prefix = self._make_prefix(event.id)

        objects = await self._list_get_objects(prefix)
        recordings = self._list_map_objects(objects)
        recordings = await self._list_filter_recordings(
            recordings, event, request.after, request.before
        )
        recordings = self._list_sort_recordings(recordings, request.order)

        count = len(recordings)

        recordings = self._list_pick_recordings(
            recordings, request.limit, request.offset
        )

        return m.ListResponse(
            count=count,
            limit=request.limit,
            offset=request.offset,
            recordings=recordings,
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a recording."""
        event = await self._get_event(request.event)

        if not event:
            raise e.EventNotFoundError(request.event)

        if event.type != bm.EventType.live:
            raise e.BadEventTypeError(event.type)

        instance = await self._get_instance(event, request.start)

        if not instance:
            raise e.InstanceNotFoundError(event.id, request.start)

        key = self._make_key(event.id, instance.start)

        download_request = em.DownloadRequest(name=key)

        with (
            self._handle_errors(),
            self._handle_not_found(event.id, instance.start),
        ):
            download_response = await self._emerald.download(download_request)

        try:
            content_type = self._parse_content_type(download_response.content.type)

            if content_type is None:
                raise e.RecordingNotFoundError(event.id, instance.start)

            return m.DownloadResponse(
                content=m.DownloadContent(
                    type=content_type,
                    size=download_response.content.size,
                    tag=download_response.content.tag,
                    modified=download_response.content.modified,
                    data=download_response.content.data,
                )
            )
        except:
            await download_response.content.data.aclose()
            raise

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload a recording."""
        event = await self._get_event(request.event)

        if not event:
            raise e.EventNotFoundError(request.event)

        if event.type != bm.EventType.live:
            raise e.BadEventTypeError(event.type)

        instance = await self._get_instance(event, request.start)

        if not instance:
            raise e.InstanceNotFoundError(event.id, request.start)

        if not ContentTypeChecker().check(request.content.type):
            raise e.UnsupportedContentTypeError(request.content.type)

        key = self._make_key(event.id, instance.start)

        upload_request = em.UploadRequest(
            name=key,
            content=em.UploadContent(
                type=str(request.content.type), data=request.content.data
            ),
        )

        with self._handle_errors():
            await self._emerald.upload(upload_request)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a recording."""
        event = await self._get_event(request.event)

        if not event:
            raise e.EventNotFoundError(request.event)

        if event.type != bm.EventType.live:
            raise e.BadEventTypeError(event.type)

        instance = await self._get_instance(event, request.start)

        if not instance:
            raise e.InstanceNotFoundError(event.id, request.start)

        key = self._make_key(event.id, instance.start)

        get_request = em.GetRequest(name=key)

        with (
            self._handle_errors(),
            self._handle_not_found(event.id, instance.start),
        ):
            get_response = await self._emerald.get(get_request)

        if not self._parse_content_type(get_response.object.type):
            raise e.RecordingNotFoundError(event.id, instance.start)

        delete_request = em.DeleteRequest(name=key)

        with (
            self._handle_errors(),
            self._handle_not_found(event.id, instance.start),
        ):
            await self._emerald.delete(delete_request)

        return m.DeleteResponse()
