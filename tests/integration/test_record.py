from datetime import datetime

import pytest
from litestar.status_codes import HTTP_201_CREATED
from litestar.testing import AsyncTestClient


@pytest.fixture(scope="session")
def data() -> dict:
    """Reusable data."""

    return {
        "event": {
            "show": {
                "label": "foo",
            },
            "start": None,
            "end": None,
        },
    }


async def test_post(client: AsyncTestClient, data: dict) -> None:
    """Test if POST /record returns correct response."""

    async with client as client:
        response = await client.post("/record", json=data)

    assert response.status_code == HTTP_201_CREATED

    data = response.json()
    assert "token" in data
    assert "expiresAt" in data

    token = data["token"]
    assert isinstance(token, str)
    assert len(token) > 0

    expires_at = data["expiresAt"]
    assert isinstance(expires_at, str)
    assert datetime.fromisoformat(expires_at)
