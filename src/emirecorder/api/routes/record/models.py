from pydantic import Field

from emirecorder.models.base import SerializableModel
from emirecorder.models.data import RecordingCredentials, RecordingRequest


class PostRequest(SerializableModel):
    """Request for POST method."""

    request: RecordingRequest = Field(
        ...,
        title="PostRequest.Request",
        description="Request for a recording.",
    )


class PostResponse(SerializableModel):
    """Response for POST method."""

    credentials: RecordingCredentials = Field(
        ...,
        title="PostResponse.Credentials",
        description="Credentials for the recording.",
    )
