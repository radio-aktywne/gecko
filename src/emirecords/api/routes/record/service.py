from collections.abc import Generator
from contextlib import contextmanager

from emirecords.api.routes.record import errors as e
from emirecords.api.routes.record import models as m
from emirecords.services.recording import errors as re
from emirecords.services.recording import models as rm
from emirecords.services.recording.service import RecordingService


class Service:
    """Service for the record endpoint."""

    def __init__(self, recording: RecordingService) -> None:
        self._recording = recording

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except re.InstanceNotFoundError as ex:
            raise e.ValidationError(str(ex)) from ex
        except re.NoPortsAvailableError as ex:
            raise e.ServiceBusyError(str(ex)) from ex
        except re.EmishowsError as ex:
            raise e.EmishowsError(str(ex)) from ex
        except re.ServiceError as ex:
            raise e.ServiceError(str(ex)) from ex

    async def record(self, request: m.RecordRequest) -> m.RecordResponse:
        """Start a recording stream."""

        event = request.data.event
        format = request.data.format

        req = rm.RecordRequest(
            event=event,
            format=format,
        )

        with self._handle_errors():
            res = await self._recording.record(req)

        credentials = res.credentials
        port = res.port

        credentials = m.Credentials.map(credentials)
        data = m.RecordResponseData(
            credentials=credentials,
            port=port,
        )
        return m.RecordResponse(
            data=data,
        )
