from litestar import Controller as BaseController
from litestar import post
from litestar.di import Provide
from litestar.response import Response

from emirecords.api.exceptions import ConflictException, UnprocessableContentException
from emirecords.api.routes.record.errors import (
    InstanceNotFoundError,
    RecorderBusyError,
)
from emirecords.api.routes.record.models import RecordRequest, RecordResponse
from emirecords.api.routes.record.service import Service
from emirecords.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(state.recorder)

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the record endpoint."""

    dependencies = DependenciesBuilder().build()

    @post(
        summary="Request a recording",
        description="Request a recording for a given event.",
        raises=[ConflictException, UnprocessableContentException],
    )
    async def record(
        self, data: RecordRequest, service: Service
    ) -> Response[RecordResponse]:
        try:
            response = await service.record(data)
        except InstanceNotFoundError as error:
            raise UnprocessableContentException(extra=error.message) from error
        except RecorderBusyError as error:
            raise ConflictException(extra=error.message) from error

        return Response(response)
