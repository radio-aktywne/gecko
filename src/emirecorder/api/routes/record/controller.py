from litestar import Controller as BaseController
from litestar import Response, post
from litestar.di import Provide

from emirecorder.api.routes.record.models import PostRequest, PostResponse
from emirecorder.api.routes.record.service import RecordService
from emirecorder.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> RecordService:
        return RecordService(state.config)

    def build(self) -> dict[str, object]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the record endpoint."""

    dependencies = DependenciesBuilder().build()

    @post(
        summary="Request a recording",
        description="Request a recording for a given event and return the credentials used to connect to the stream",
    )
    async def post(
        self, data: PostRequest, service: RecordService
    ) -> Response[PostResponse]:
        credentials = await service.record(data.request)
        content = PostResponse(credentials=credentials)
        return Response(content)
