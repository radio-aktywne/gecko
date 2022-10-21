from starlite import Controller, State, post

from emirecorder.api.paths.record.models import RecordRequest, RecordResponse


class RecordController(Controller):
    path = None

    @post()
    async def record(
        self, state: State, data: RecordRequest
    ) -> RecordResponse:
        return RecordResponse(token=state.stream_manager.record(data.event))
