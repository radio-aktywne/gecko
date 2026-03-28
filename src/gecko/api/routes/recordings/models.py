from collections.abc import AsyncIterator, Sequence
from datetime import datetime
from typing import Self
from uuid import UUID

from gecko.models.base import SerializableModel, datamodel
from gecko.services.recordings import models as rm
from gecko.utils.time import NaiveDatetime


class Recording(SerializableModel):
    """Recording data."""

    event: UUID
    """Identifier of the event."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""

    @classmethod
    def map(cls, recording: rm.Recording) -> Self:
        """Map to internal representation."""
        return cls(event=recording.event, start=recording.start)


class RecordingList(SerializableModel):
    """List of recordings."""

    count: int
    """Total number of recordings that match the request."""

    limit: int | None
    """Maximum number of returned recordings."""

    offset: int | None
    """Number of skipped recordings."""

    recordings: Sequence[Recording]
    """List of recordings."""


type ListRequestEvent = UUID

type ListRequestAfter = NaiveDatetime | None

type ListRequestBefore = NaiveDatetime | None

type ListRequestLimit = int | None

type ListRequestOffset = int | None

type ListRequestOrder = rm.ListOrder | None

type ListResponseResults = RecordingList

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
    """Request to list recordings."""

    event: ListRequestEvent
    """Identifier of the event to list recordings for."""

    after: ListRequestAfter
    """Only list recordings after or at this datetime (in event timezone)."""

    before: ListRequestBefore
    """Only list recordings strictly before this datetime (in event timezone)."""

    limit: ListRequestLimit
    """Maximum number of recordings to return."""

    offset: ListRequestOffset
    """Number of recordings to skip."""

    order: ListRequestOrder
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing recordings."""

    results: ListResponseResults
    """List of recordings."""


@datamodel
class DownloadRequest:
    """Request to download a recording."""

    event: DownloadRequestEvent
    """Identifier of the event."""

    start: DownloadRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class DownloadResponse:
    """Response for downloading a recording."""

    type: DownloadResponseType
    """Type of the recording data."""

    size: DownloadResponseSize
    """Size of the recording in bytes."""

    tag: DownloadResponseTag
    """ETag of the recording data."""

    modified: DownloadResponseModified
    """Datetime when the recording was last modified."""

    data: DownloadResponseData
    """Data of the recording."""


@datamodel
class HeadDownloadRequest:
    """Request to download recording headers."""

    event: HeadDownloadRequestEvent
    """Identifier of the event."""

    start: HeadDownloadRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class HeadDownloadResponse:
    """Response for downloading recording headers."""

    type: HeadDownloadResponseType
    """Type of the recording data."""

    size: HeadDownloadResponseSize
    """Size of the recording in bytes."""

    tag: HeadDownloadResponseTag
    """ETag of the recording data."""

    modified: HeadDownloadResponseModified
    """Datetime when the recording was last modified."""


@datamodel
class UploadRequest:
    """Request to upload a recording."""

    event: UploadRequestEvent
    """Identifier of the event."""

    start: UploadRequestStart
    """Start datetime of the event instance in event timezone."""

    type: UploadRequestType
    """Type of the recording data."""

    data: UploadRequestData
    """Data of the recording."""


@datamodel
class UploadResponse:
    """Response for uploading a recording."""


@datamodel
class DeleteRequest:
    """Request to delete a recording."""

    event: DeleteRequestEvent
    """Identifier of the event."""

    start: DeleteRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class DeleteResponse:
    """Response for deleting a recording."""
