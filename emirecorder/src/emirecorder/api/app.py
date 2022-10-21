from starlite import State, Starlite, WebSocketException, CORSConfig

from emirecorder.api.paths.router import router
from emirecorder.config import Config
from emirecorder.stream.management import StreamManager


def build(config: Config) -> Starlite:
    async def setup(state: State) -> None:
        state.stream_manager = StreamManager(config)
        state.sockets = {}

    async def cleanup(state: State) -> None:
        for uid, socket in state.sockets.items():
            try:
                await socket.close()
            except (ConnectionError, WebSocketException):
                pass
            state.sockets.pop(uid, None)

    return Starlite(
        route_handlers=[router],
        cors_config=CORSConfig(
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        on_startup=[setup],
        on_shutdown=[cleanup],
    )
