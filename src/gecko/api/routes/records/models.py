from collections.abc import AsyncIterator, Sequence
from datetime import datetime
from typing import Self
from uuid import UUID

from gecko.models.base import SerializableModel, datamodel
from gecko.services.records import models as rm
from gecko.utils.time import NaiveDatetime


class Record(SerializableModel):
    """Record data."""

    event: UUID
    """Identifier of the event."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""

    @classmethod
    def map(cls, record: rm.Record) -> Self:
        """Map to internal representation."""
        return cls(event=record.event, start=record.start)


class RecordList(SerializableModel):
    """List of records."""

    count: int
    """Total number of records that match the request."""

    limit: int | None
    """Maximum number of returned records."""

    offset: int | None
    """Number of skipped records."""

    records: Sequence[Record]
    """List of records."""


type ListRequestEvent = UUID

type ListRequestAfter = NaiveDatetime | None

type ListRequestBefore = NaiveDatetime | None

type ListRequestLimit = int | None

type ListRequestOffset = int | None

type ListRequestOrder = rm.ListOrder | None

type ListResponseResults = RecordList

type DownloadRequestEvent = UUID

type DownloadRequestStart = NaiveDatetime

type DownloadResponseType = str

type DownloadResponseSize = int

type DownloadResponseTag = str

type DownloadResponseModified = datetime

type DownloadResponseData = AsyncIterator[bytes]

type HeadDownloadRequestEvent = UUID

type HeadDownloadRequestStart = NaiveDatetime

type HeadDownloadResponseType = str

type HeadDownloadResponseSize = int

type HeadDownloadResponseTag = str

type HeadDownloadResponseModified = datetime

type UploadRequestEvent = UUID

type UploadRequestStart = NaiveDatetime

type UploadRequestType = str

type UploadRequestData = AsyncIterator[bytes]

type DeleteRequestEvent = UUID

type DeleteRequestStart = NaiveDatetime


@datamodel
class ListRequest:
    """Request to list records."""

    event: ListRequestEvent
    """Identifier of the event to list records for."""

    after: ListRequestAfter
    """Only list records after this datetime (in event timezone)."""

    before: ListRequestBefore
    """Only list records before this datetime (in event timezone)."""

    limit: ListRequestLimit
    """Maximum number of records to return."""

    offset: ListRequestOffset
    """Number of records to skip."""

    order: ListRequestOrder
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing records."""

    results: ListResponseResults
    """List of records."""


@datamodel
class DownloadRequest:
    """Request to download a record."""

    event: DownloadRequestEvent
    """Identifier of the event."""

    start: DownloadRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class DownloadResponse:
    """Response for downloading a record."""

    type: DownloadResponseType
    """Type of the record data."""

    size: DownloadResponseSize
    """Size of the record in bytes."""

    tag: DownloadResponseTag
    """ETag of the record data."""

    modified: DownloadResponseModified
    """Datetime when the record was last modified."""

    data: DownloadResponseData
    """Data of the record."""


@datamodel
class HeadDownloadRequest:
    """Request to download record headers."""

    event: HeadDownloadRequestEvent
    """Identifier of the event."""

    start: HeadDownloadRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class HeadDownloadResponse:
    """Response for downloading record headers."""

    type: HeadDownloadResponseType
    """Type of the record data."""

    size: HeadDownloadResponseSize
    """Size of the record in bytes."""

    tag: HeadDownloadResponseTag
    """ETag of the record data."""

    modified: HeadDownloadResponseModified
    """Datetime when the record was last modified."""


@datamodel
class UploadRequest:
    """Request to upload a record."""

    event: UploadRequestEvent
    """Identifier of the event."""

    start: UploadRequestStart
    """Start datetime of the event instance in event timezone."""

    type: UploadRequestType
    """Type of the record data."""

    data: UploadRequestData
    """Data of the record."""


@datamodel
class UploadResponse:
    """Response for uploading a record."""


@datamodel
class DeleteRequest:
    """Request to delete a record."""

    event: DeleteRequestEvent
    """Identifier of the event."""

    start: DeleteRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class DeleteResponse:
    """Response for deleting a record."""
