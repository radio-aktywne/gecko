from datetime import datetime

import pytest
from litestar.status_codes import HTTP_201_CREATED
from litestar.testing import AsyncTestClient


@pytest.fixture(scope="session")
def data() -> dict:
    """Reusable data."""

    return {
        "request": {
            "event": {
                "show": {
                    "label": "foo",
                },
                "start": None,
                "end": None,
            },
        },
    }


async def test_post(client: AsyncTestClient, data: dict) -> None:
    """Test if POST /record returns correct response."""

    async with client as client:
        response = await client.post("/record", json=data)

    assert response.status_code == HTTP_201_CREATED

    data = response.json()
    assert "credentials" in data

    credentials = data["credentials"]
    assert "token" in credentials
    assert "expiresAt" in credentials

    token = credentials["token"]
    assert isinstance(token, str)
    assert len(token) > 0

    expires_at = credentials["expiresAt"]
    assert isinstance(expires_at, str)
    assert datetime.fromisoformat(expires_at)
