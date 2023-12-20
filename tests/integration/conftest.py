import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.testing import AsyncTestClient

from emirecorder.api.app import AppBuilder
from emirecorder.config.builder import ConfigBuilder
from emirecorder.config.models import Config
from tests.utils.containers import AsyncDockerContainer, ContainerWaiter


@pytest.fixture(scope="session")
def config() -> Config:
    """Loaded configuration."""

    return ConfigBuilder().build()


@pytest.fixture(scope="session")
def app(config: Config) -> Litestar:
    """Reusable application."""

    return AppBuilder(config).build()


@pytest_asyncio.fixture(scope="session")
async def emiarchive(config: Config) -> AsyncDockerContainer:
    """Emiarchive container."""

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/emiarchive:latest",
        network="host",
    )

    async with container as container:
        # Wait for emiarchive to start.
        waiter = ContainerWaiter(
            container,
            [
                "./scripts/shell.sh",
                "mc",
                "config",
                "host",
                "add",
                "minio",
                f"http://localhost:{config.emiarchive.port}",
                config.emiarchive.user,
                config.emiarchive.password,
            ],
        )
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def client(app: Litestar, emiarchive: AsyncDockerContainer) -> AsyncTestClient:
    """Reusable test client."""

    async with AsyncTestClient(app=app) as client:
        yield client
