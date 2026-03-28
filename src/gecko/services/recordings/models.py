from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from gecko.models.base import datamodel
from gecko.services.emerald import models as em

DownloadContent = em.DownloadContent

UploadContent = em.UploadContent


class ListOrder(StrEnum):
    """Order to list recordings."""

    ASCENDING = "asc"
    DESCENDING = "desc"


@datamodel
class Recording:
    """Recording data."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start datetime of the event instance in event timezone."""


@datamodel
class ListRequest:
    """Request to list recordings."""

    event: UUID
    """Identifier of the event to list recordings for."""

    after: datetime | None
    """Only list recordings after or at this datetime (in event timezone)."""

    before: datetime | None
    """Only list recordings strictly before this datetime (in event timezone)."""

    limit: int | None
    """Maximum number of recordings to return."""

    offset: int | None
    """Number of recordings to skip."""

    order: ListOrder | None
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing recordings."""

    count: int
    """Total number of recordings that match the request."""

    limit: int | None
    """Maximum number of returned recordings."""

    offset: int | None
    """Number of skipped recordings."""

    recordings: Sequence[Recording]
    """List of recordings."""


@datamodel
class DownloadRequest:
    """Request to download a recording."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start datetime of the event instance in event timezone."""


@datamodel
class DownloadResponse:
    """Response for downloading a recording."""

    content: DownloadContent
    """Content of the recording."""


@datamodel
class UploadRequest:
    """Request to upload a recording."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start datetime of the event instance in event timezone."""

    content: UploadContent
    """Content of the recording."""


@datamodel
class UploadResponse:
    """Response for uploading a recording."""


@datamodel
class DeleteRequest:
    """Request to delete a recording."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start datetime of the event instance in event timezone."""


@datamodel
class DeleteResponse:
    """Response for deleting a recording."""
