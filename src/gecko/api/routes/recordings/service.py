from collections.abc import Generator
from contextlib import contextmanager

from gecko.api.routes.recordings import errors as e
from gecko.api.routes.recordings import models as m
from gecko.services.recordings import errors as re
from gecko.services.recordings import models as rm
from gecko.services.recordings.service import RecordingsService


class Service:
    """Service for the recordings endpoint."""

    def __init__(self, recordings: RecordingsService) -> None:
        self._recordings = recordings

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except re.EventNotFoundError as ex:
            raise e.EventNotFoundError from ex
        except re.BadEventTypeError as ex:
            raise e.BadEventTypeError from ex
        except re.InstanceNotFoundError as ex:
            raise e.InstanceNotFoundError from ex
        except re.RecordingNotFoundError as ex:
            raise e.RecordingNotFoundError from ex
        except re.BeaverError as ex:
            raise e.BeaverError from ex
        except re.EmeraldError as ex:
            raise e.EmeraldError from ex
        except re.ServiceError as ex:
            raise e.ServiceError from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List recordings."""
        list_request = rm.ListRequest(
            event=request.event,
            after=request.after,
            before=request.before,
            limit=request.limit,
            offset=request.offset,
            order=request.order,
        )

        with self._handle_errors():
            list_response = await self._recordings.list(list_request)

        return m.ListResponse(
            results=m.RecordingList(
                count=list_response.count,
                limit=request.limit,
                offset=request.offset,
                recordings=[
                    m.Recording.map(recording) for recording in list_response.recordings
                ],
            )
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a recording."""
        download_request = rm.DownloadRequest(event=request.event, start=request.start)

        with self._handle_errors():
            download_response = await self._recordings.download(download_request)

        return m.DownloadResponse(
            type=download_response.content.type,
            size=download_response.content.size,
            tag=download_response.content.tag,
            modified=download_response.content.modified,
            data=download_response.content.data,
        )

    async def headdownload(
        self, request: m.HeadDownloadRequest
    ) -> m.HeadDownloadResponse:
        """Download recording headers."""
        download_request = rm.DownloadRequest(event=request.event, start=request.start)

        with self._handle_errors():
            download_response = await self._recordings.download(download_request)

        return m.HeadDownloadResponse(
            type=download_response.content.type,
            size=download_response.content.size,
            tag=download_response.content.tag,
            modified=download_response.content.modified,
        )

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload a recording."""
        upload_request = rm.UploadRequest(
            event=request.event,
            start=request.start,
            content=rm.UploadContent(type=request.type, data=request.data),
        )

        with self._handle_errors():
            await self._recordings.upload(upload_request)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a recording."""
        delete_request = rm.DeleteRequest(event=request.event, start=request.start)

        with self._handle_errors():
            await self._recordings.delete(delete_request)

        return m.DeleteResponse()
