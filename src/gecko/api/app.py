from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

from litestar import Litestar
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol

from gecko.api.lifespans import SuppressHTTPXLoggingLifespan, TestLifespan
from gecko.api.openapi import OpenAPIConfigBuilder
from gecko.api.plugins.pydantic import PydanticPlugin
from gecko.api.routes.router import router
from gecko.config.models import Config
from gecko.services.beaver.service import BeaverService
from gecko.services.emerald.service import EmeraldService
from gecko.state import State


class AppBuilder:
    """Builds the app.

    Args:
        config: Config object.

    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_lifespan(
        self,
    ) -> Sequence[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            TestLifespan,
            SuppressHTTPXLoggingLifespan,
        ]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfigBuilder().build()

    def _build_plugins(self) -> Sequence[PluginProtocol]:
        return [
            ChannelsPlugin(backend=MemoryChannelsBackend(), channels=["events"]),
            PydanticPlugin(),
        ]

    def _build_initial_state(self) -> State:
        return State(
            {
                "config": self._config,
                "beaver": BeaverService(config=self._config.beaver),
                "emerald": EmeraldService(config=self._config.emerald),
            }
        )

    def build(self) -> Litestar:
        """Build the app."""
        return Litestar(
            route_handlers=[router],
            debug=self._config.debug,
            lifespan=self._build_lifespan(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
        )
