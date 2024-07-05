from emirecords.api.routes.record import errors as e
from emirecords.api.routes.record.models import RecordRequest, RecordResponse
from emirecords.recording import errors as re
from emirecords.recording.recorder import Recorder


class Service:
    """Service for the record endpoint."""

    def __init__(self, recorder: Recorder) -> None:
        self._recorder = recorder

    async def record(self, request: RecordRequest) -> RecordResponse:
        """Starts a recording stream."""

        try:
            return await self._recorder.record(request)
        except re.InstanceNotFoundError as error:
            raise e.InstanceNotFoundError(error.message) from error
        except re.NoPortsAvailableError as error:
            raise e.RecorderBusyError(error.message) from error
        except re.RecordingError as error:
            raise e.ServiceError(error.message) from error
