import pytest
from litestar.testing import AsyncTestClient

from emirecorder.api import AppBuilder
from emirecorder.config import ConfigBuilder


@pytest.fixture(scope="session")
def client() -> AsyncTestClient:
    """Reusable test client."""

    config = ConfigBuilder().build()
    app = AppBuilder(config).build()
    return AsyncTestClient(app=app)
