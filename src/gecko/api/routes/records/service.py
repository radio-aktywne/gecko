from collections.abc import Generator
from contextlib import contextmanager

from gecko.api.routes.records import errors as e
from gecko.api.routes.records import models as m
from gecko.services.records import errors as re
from gecko.services.records import models as rm
from gecko.services.records.service import RecordsService


class Service:
    """Service for the records endpoint."""

    def __init__(self, records: RecordsService):
        self._records = records

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except re.EventNotFoundError as ex:
            raise e.EventNotFoundError(str(ex)) from ex
        except re.BadEventTypeError as ex:
            raise e.BadEventTypeError(str(ex)) from ex
        except re.InstanceNotFoundError as ex:
            raise e.InstanceNotFoundError(str(ex)) from ex
        except re.RecordNotFoundError as ex:
            raise e.RecordNotFoundError(str(ex)) from ex
        except re.BeaverError as ex:
            raise e.BeaverError(str(ex)) from ex
        except re.EmeraldError as ex:
            raise e.EmeraldError(str(ex)) from ex
        except re.ServiceError as ex:
            raise e.ServiceError(str(ex)) from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List records."""

        event = request.event
        after = request.after
        before = request.before
        limit = request.limit
        offset = request.offset
        order = request.order

        req = rm.ListRequest(
            event=event,
            after=after,
            before=before,
            limit=limit,
            offset=offset,
            order=order,
        )

        with self._handle_errors():
            res = await self._records.list(req)

        count = res.count
        records = res.records

        records = [m.Record.map(record) for record in records]
        results = m.RecordList(
            count=count,
            limit=limit,
            offset=offset,
            records=records,
        )
        return m.ListResponse(
            results=results,
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a record."""

        event = request.event
        start = request.start

        req = rm.DownloadRequest(
            event=event,
            start=start,
        )

        with self._handle_errors():
            res = await self._records.download(req)

        content = res.content

        type = content.type
        size = content.size
        tag = content.tag
        modified = content.modified
        data = content.data
        return m.DownloadResponse(
            type=type,
            size=size,
            tag=tag,
            modified=modified,
            data=data,
        )

    async def headdownload(
        self, request: m.HeadDownloadRequest
    ) -> m.HeadDownloadResponse:
        """Download record headers."""

        event = request.event
        start = request.start

        req = rm.DownloadRequest(
            event=event,
            start=start,
        )

        with self._handle_errors():
            res = await self._records.download(req)

        content = res.content

        type = content.type
        size = content.size
        tag = content.tag
        modified = content.modified
        return m.HeadDownloadResponse(
            type=type,
            size=size,
            tag=tag,
            modified=modified,
        )

    async def upload(self, request: m.UploadRequest) -> m.UploadResponse:
        """Upload a record."""

        event = request.event
        start = request.start
        type = request.type
        data = request.data

        content = rm.UploadContent(
            type=type,
            data=data,
        )
        req = rm.UploadRequest(
            event=event,
            start=start,
            content=content,
        )

        with self._handle_errors():
            await self._records.upload(req)

        return m.UploadResponse()

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete a record."""

        event = request.event
        start = request.start

        req = rm.DeleteRequest(
            event=event,
            start=start,
        )

        with self._handle_errors():
            await self._records.delete(req)

        return m.DeleteResponse()
