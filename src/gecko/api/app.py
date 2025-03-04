import logging
import warnings
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from importlib import metadata

from litestar import Litestar, Router
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol
from litestar.plugins.pydantic import PydanticPlugin
from urllib3.exceptions import InsecureRequestWarning

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

    def _get_route_handlers(self) -> list[Router]:
        return [router]

    def _get_debug(self) -> bool:
        return self._config.debug

    @asynccontextmanager
    async def _suppress_urllib_warnings_lifespan(
        self, app: Litestar
    ) -> AsyncGenerator[None]:
        with warnings.catch_warnings(
            action="ignore",
            category=InsecureRequestWarning,
        ):
            yield

    @asynccontextmanager
    async def _suppress_httpx_logging_lifespan(
        self, app: Litestar
    ) -> AsyncGenerator[None]:
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
            self._suppress_urllib_warnings_lifespan,
            self._suppress_httpx_logging_lifespan,
        ]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfig(
            # Title of the service
            title="gecko",
            # Version of the service
            version=metadata.version("gecko"),
            # Description of the service
            summary="Broadcast recordings 📼",
            # Use handler docstrings as operation descriptions
            use_handler_docstrings=True,
            # Endpoint to serve the OpenAPI docs from
            path="/schema",
        )

    def _build_pydantic_plugin(self) -> PydanticPlugin:
        return PydanticPlugin(
            # Use aliases for serialization
            prefer_alias=True,
            # Allow type coercion
            validate_strict=False,
        )

    def _build_plugins(self) -> list[PluginProtocol]:
        return [
            self._build_pydantic_plugin(),
        ]

    def _build_beaver(self) -> BeaverService:
        return BeaverService(
            config=self._config.beaver,
        )

    def _build_emerald(self) -> EmeraldService:
        return EmeraldService(
            config=self._config.emerald,
        )

    def _build_initial_state(self) -> State:
        config = self._config
        beaver = self._build_beaver()
        emerald = self._build_emerald()

        return State(
            {
                "config": config,
                "beaver": beaver,
                "emerald": emerald,
            }
        )

    def build(self) -> Litestar:
        return Litestar(
            route_handlers=self._get_route_handlers(),
            debug=self._get_debug(),
            lifespan=self._build_lifespan(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
        )
