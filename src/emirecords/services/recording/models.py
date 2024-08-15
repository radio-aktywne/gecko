from datetime import datetime
from enum import StrEnum
from uuid import UUID

from emirecords.models.base import datamodel


class Format(StrEnum):
    """Audio format."""

    OGG = "ogg"


@datamodel
class Credentials:
    """Credentials for a recording stream."""

    token: str
    """Token to use to connect to the stream."""

    expires_at: datetime
    """Time in UTC at which the token expires if not used."""


@datamodel
class RecordRequest:
    """Request to start recording."""

    event: UUID
    """Identifier of the event to record."""

    format: Format
    """Format of the recording."""


@datamodel
class RecordResponse:
    """Response for starting a recording."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""

    port: int
    """Port to use to connect to the stream."""
