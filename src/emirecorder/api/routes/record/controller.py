from litestar import Controller as BaseController
from litestar import post
from litestar.di import Provide

from emirecorder.api.routes.record.models import RecordRequest, RecordResponse
from emirecorder.api.routes.record.service import Service
from emirecorder.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(state.config)

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the record endpoint."""

    dependencies = DependenciesBuilder().build()

    @post(
        summary="Request a recording",
        description="Request a recording for a given event and return the credentials used to connect to the stream.",
    )
    async def record(self, data: RecordRequest, service: Service) -> RecordResponse:
        return await service.record(data)
