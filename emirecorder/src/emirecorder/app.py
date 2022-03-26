from starlite import Starlite, State

from emirecorder.paths.router import router
from emirecorder.stream.management import StreamManager


async def setup(state: State) -> None:
    state.stream_manager = StreamManager()


async def cleanup(state: State) -> None:
    pass


app = Starlite(
    route_handlers=[router], on_startup=[setup], on_shutdown=[cleanup]
)
