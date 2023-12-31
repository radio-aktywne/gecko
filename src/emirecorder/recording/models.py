from typing import Literal
from uuid import UUID

from pydantic import Field, NaiveDatetime

from emirecorder.models.base import SerializableModel

Format = Literal["ogg"]


class Request(SerializableModel):
    """Request for a recording."""

    event: UUID = Field(
        ...,
        title="Request.Event",
        description="Identifier of the event to record.",
    )
    format: Format = Field(
        "ogg",
        title="Request.Format",
        description="Format of the recording.",
    )


class Credentials(SerializableModel):
    """Credentials for a recording stream."""

    token: str = Field(
        ...,
        title="Credentials.Token",
        description="Token to use to connect to the stream.",
    )
    expires_at: NaiveDatetime = Field(
        ...,
        title="Credentials.ExpiresAt",
        description="Time in UTC at which the token expires if not used.",
    )


class Response(SerializableModel):
    """Response to a recording request."""

    credentials: Credentials = Field(
        ...,
        title="Response.Credentials",
        description="Credentials to use to connect to the stream.",
    )
    host: str = Field(
        ...,
        title="Response.Host",
        description="Host to use to connect to the stream.",
    )
    port: int = Field(
        ...,
        title="Response.Port",
        description="Port to use to connect to the stream.",
    )
