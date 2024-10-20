from datetime import datetime
from enum import StrEnum
from uuid import UUID

from gecko.models.base import datamodel
from gecko.services.emerald import models as em

DownloadContent = em.DownloadContent

UploadContent = em.UploadContent


class ListOrder(StrEnum):
    """Order to list records."""

    ASCENDING = "asc"
    DESCENDING = "desc"


@datamodel
class Record:
    """Record data."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start time of the event instance in event timezone."""


@datamodel
class ListRequest:
    """Request to list records."""

    event: UUID
    """Identifier of the event to list records for."""

    after: datetime | None
    """Only list records after this time (in event timezone)."""

    before: datetime | None
    """Only list records before this date (in event timezone)."""

    limit: int | None
    """Maximum number of records to return."""

    offset: int | None
    """Number of records to skip."""

    order: ListOrder | None
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing records."""

    count: int
    """Total number of records that match the request."""

    limit: int | None
    """Maximum number of returned records."""

    offset: int | None
    """Number of skipped records."""

    records: list[Record]
    """List of records."""


@datamodel
class DownloadRequest:
    """Request to download a record."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start time of the event instance in event timezone."""


@datamodel
class DownloadResponse:
    """Response for downloading a record."""

    content: DownloadContent
    """Content of the record."""


@datamodel
class UploadRequest:
    """Request to upload a record."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start time of the event instance in event timezone."""

    content: UploadContent
    """Content of the record."""


@datamodel
class UploadResponse:
    """Response for uploading a record."""

    pass


@datamodel
class DeleteRequest:
    """Request to delete a record."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start time of the event instance in event timezone."""


@datamodel
class DeleteResponse:
    """Response for deleting a record."""

    pass
