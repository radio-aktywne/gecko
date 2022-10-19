from starlite import Starlite, State

from emirecorder.config import Config
from emirecorder.paths.router import router
from emirecorder.stream.management import StreamManager


def build_app(config: Config) -> Starlite:
    async def setup(state: State) -> None:
        state.stream_manager = StreamManager(config)

    async def cleanup(state: State) -> None:
        pass

    return Starlite(
        route_handlers=[router], on_startup=[setup], on_shutdown=[cleanup]
    )
