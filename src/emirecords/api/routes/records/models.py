from collections.abc import AsyncIterator
from datetime import datetime
from uuid import UUID

from emirecords.models.base import SerializableModel, datamodel
from emirecords.services.records import models as rm
from emirecords.utils.time import NaiveDatetime


class Record(SerializableModel):
    """Record data."""

    event: UUID
    """Identifier of the event."""

    start: NaiveDatetime
    """Start time of the event instance in event timezone."""

    @staticmethod
    def map(record: rm.Record) -> "Record":
        return Record(
            event=record.event,
            start=record.start,
        )


class RecordList(SerializableModel):
    """List of records."""

    count: int
    """Total number of records that match the request."""

    limit: int | None
    """Maximum number of returned records."""

    offset: int | None
    """Number of skipped records."""

    records: list[Record]
    """List of records."""


ListRequestEvent = UUID

ListRequestAfter = NaiveDatetime | None

ListRequestBefore = NaiveDatetime | None

ListRequestLimit = int | None

ListRequestOffset = int | None

ListRequestOrder = rm.ListOrder | None

ListResponseResults = RecordList

DownloadRequestEvent = UUID

DownloadRequestStart = NaiveDatetime

DownloadResponseType = str

DownloadResponseSize = int

DownloadResponseTag = str

DownloadResponseModified = datetime

DownloadResponseData = AsyncIterator[bytes]

HeadDownloadRequestEvent = UUID

HeadDownloadRequestStart = NaiveDatetime

HeadDownloadResponseType = str

HeadDownloadResponseSize = int

HeadDownloadResponseTag = str

HeadDownloadResponseModified = datetime

UploadRequestEvent = UUID

UploadRequestStart = NaiveDatetime

UploadRequestType = str

UploadRequestData = AsyncIterator[bytes]

DeleteRequestEvent = UUID

DeleteRequestStart = NaiveDatetime


@datamodel
class ListRequest:
    """Request to list records."""

    event: ListRequestEvent
    """Identifier of the event to list records for."""

    after: ListRequestAfter
    """Only list records after this time (in event timezone)."""

    before: ListRequestBefore
    """Only list records before this date (in event timezone)."""

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
    """Start time of the event instance in event timezone."""


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
    """Date and time when the record was last modified."""

    data: DownloadResponseData
    """Data of the record."""


@datamodel
class HeadDownloadRequest:
    """Request to download record headers."""

    event: HeadDownloadRequestEvent
    """Identifier of the event."""

    start: HeadDownloadRequestStart
    """Start time of the event instance in event timezone."""


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
    """Date and time when the record was last modified."""


@datamodel
class UploadRequest:
    """Request to upload a record."""

    event: UploadRequestEvent
    """Identifier of the event."""

    start: UploadRequestStart
    """Start time of the event instance in event timezone."""

    type: UploadRequestType
    """Type of the record data."""

    data: UploadRequestData
    """Data of the record."""


@datamodel
class UploadResponse:
    """Response for uploading a record."""

    pass


@datamodel
class DeleteRequest:
    """Request to delete a record."""

    event: DeleteRequestEvent
    """Identifier of the event."""

    start: DeleteRequestStart
    """Start time of the event instance in event timezone."""


@datamodel
class DeleteResponse:
    """Response for deleting a record."""

    pass
