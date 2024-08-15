from uuid import UUID

from pydantic import Field

from emirecords.models.base import SerializableModel, datamodel, serializable
from emirecords.services.recording import models as rm


@serializable
@datamodel
class Credentials(rm.Credentials):
    @staticmethod
    def map(credentials: rm.Credentials) -> "Credentials":
        return Credentials(**vars(credentials))


class RecordRequestData(SerializableModel):
    """Data for a record request."""

    event: UUID
    """Identifier of the event to record."""

    format: rm.Format = rm.Format.OGG
    """Format of the recording."""


class RecordResponseData(SerializableModel):
    """Data for a record response."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""

    port: int = Field(..., ge=1, le=65535)
    """Port to use to connect to the stream."""


@datamodel
class RecordRequest:
    """Request to record."""

    data: RecordRequestData
    """Data for the request."""


@datamodel
class RecordResponse:
    """Response for record."""

    data: RecordResponseData
    """Data for the response."""
