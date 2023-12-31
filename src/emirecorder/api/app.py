import logging
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from importlib import metadata
from typing import AsyncGenerator, Callable

from litestar import Litestar, Router
from litestar.contrib.pydantic import PydanticPlugin
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol

from emirecorder.api.routes.router import router
from emirecorder.config.models import Config
from emirecorder.emishows.service import EmishowsService
from emirecorder.locks.asyncio import AsyncioLock
from emirecorder.recording.recorder import Recorder
from emirecorder.state import State
from emirecorder.stores.memory import MemoryStore


class AppBuilder:
    """Builds the app.

    Args:
        config: Config object.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def _get_route_handlers(self) -> list[Router]:
        return [router]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfig(
            title="emirecorder app",
            version=metadata.version("emirecorder"),
            description="Emission recording 🎥",
        )

    def _build_pydantic_plugin(self) -> PydanticPlugin:
        return PydanticPlugin(
            prefer_alias=True,
        )

    def _build_plugins(self) -> list[PluginProtocol]:
        return [
            self._build_pydantic_plugin(),
        ]

    def _build_emishows(self) -> EmishowsService:
        return EmishowsService(config=self._config.emishows)

    def _build_recorder(self, emishows: EmishowsService) -> Recorder:
        return Recorder(
            config=self._config,
            store=MemoryStore[set[int]](set()),
            lock=AsyncioLock(),
            emishows=emishows,
        )

    def _build_initial_state(self) -> State:
        emishows = self._build_emishows()
        recorder = self._build_recorder(emishows)

        return State(
            {
                "config": self._config,
                "emishows": emishows,
                "recorder": recorder,
            }
        )

    @asynccontextmanager
    async def _suppress_httpx_logging_lifespan(
        self, app: Litestar
    ) -> AsyncGenerator[None, None]:
        logger = logging.getLogger("httpx")
        disabled = logger.disabled
        logger.disabled = True

        try:
            yield
        finally:
            logger.disabled = disabled

    def _build_lifespan(
        self,
    ) -> list[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            self._suppress_httpx_logging_lifespan,
        ]

    def build(self) -> Litestar:
        return Litestar(
            route_handlers=self._get_route_handlers(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
            lifespan=self._build_lifespan(),
        )
