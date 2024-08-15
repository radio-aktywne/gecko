import asyncio
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from pylocks.base import Lock
from pystores.base import Store
from pystreams.stream import Stream
from zoneinfo import ZoneInfo

from emirecords.config.models import Config
from emirecords.services.emishows import errors as ee
from emirecords.services.emishows import models as em
from emirecords.services.emishows.service import EmishowsService
from emirecords.services.recording import errors as e
from emirecords.services.recording import models as m
from emirecords.services.recording.runner import Runner
from emirecords.utils.time import naiveutcnow


class RecordingService:
    """Service to manage recording."""

    def __init__(
        self,
        config: Config,
        store: Store[set[int]],
        lock: Lock,
        emishows: EmishowsService,
    ) -> None:
        self._config = config
        self._store = store
        self._lock = lock
        self._emishows = emishows

    def _get_reference_time(self) -> datetime:
        return naiveutcnow()

    def _get_time_window(self, reference: datetime) -> tuple[datetime, datetime]:
        start = reference - self._config.recording.window
        end = reference + self._config.recording.window

        return start, end

    async def _get_schedule(
        self, event: UUID, start: datetime, end: datetime
    ) -> em.Schedule:
        req = em.ListRequest(
            start=start,
            end=end,
            limit=None,
            offset=None,
            where={
                "id": str(event),
            },
            include=None,
            order=None,
        )

        try:
            res = await self._emishows.schedule.list(req)
        except ee.ServiceError as ex:
            raise e.EmishowsError(str(ex)) from ex

        results = res.results
        schedules = results.schedules

        schedule = next(
            (schedule for schedule in schedules if schedule.event.id == event),
            None,
        )

        if schedule is None:
            raise e.InstanceNotFoundError(event)

        return schedule

    def _find_nearest_instance(
        self, reference: datetime, schedule: em.Schedule
    ) -> em.EventInstance:
        def _compare(instance: em.EventInstance) -> timedelta:
            tz = ZoneInfo(schedule.event.timezone)
            start = instance.start.replace(tzinfo=tz)
            start = start.astimezone(timezone.utc).replace(tzinfo=None)
            return abs(start - reference)

        instance = min(schedule.instances, key=_compare, default=None)

        if instance is None:
            raise e.InstanceNotFoundError(schedule.event.id)

        return instance

    def _generate_token(self) -> str:
        return secrets.token_hex(16)

    def _get_token_expiry(self) -> datetime:
        return naiveutcnow() + self._config.recording.timeout

    def _generate_credentials(self) -> m.Credentials:
        return m.Credentials(
            token=self._generate_token(),
            expires_at=self._get_token_expiry(),
        )

    async def _reserve_port(self) -> int:
        async with self._lock:
            used = await self._store.get()
            available = self._config.server.ports.srt - used

            if not available:
                raise e.NoPortsAvailableError()

            port = available.pop()

            await self._store.set(used | {port})

        return port

    async def _free_port(self, port: int) -> None:
        async with self._lock:
            used = await self._store.get()
            used.remove(port)
            await self._store.set(used)

    async def _watch_stream(self, stream: Stream, port: int) -> None:
        try:
            await stream.wait()
        finally:
            await self._free_port(port)

    async def _run(
        self,
        event: em.Event,
        instance: em.EventInstance,
        credentials: m.Credentials,
        port: int,
        format: m.Format,
    ) -> None:
        runner = Runner(self._config)
        stream = await runner.run(
            event=event,
            instance=instance,
            credentials=credentials,
            port=port,
            format=format,
        )

        asyncio.create_task(self._watch_stream(stream, port))

    async def record(self, request: m.RecordRequest) -> m.RecordResponse:
        """Starts a recording stream."""

        event = request.event
        format = request.format

        reference = self._get_reference_time()
        start, end = self._get_time_window(reference)

        schedule = await self._get_schedule(event, start, end)
        event = schedule.event
        instance = self._find_nearest_instance(reference, schedule)

        credentials = self._generate_credentials()
        port = await self._reserve_port()

        try:
            await self._run(event, instance, credentials, port, format)
        except Exception:
            await self._free_port(port)
            raise

        return m.RecordResponse(
            credentials=credentials,
            port=port,
        )
