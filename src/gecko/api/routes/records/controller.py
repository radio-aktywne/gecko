from collections.abc import AsyncGenerator, Mapping
from typing import Annotated

from litestar import Controller as BaseController
from litestar import Request, handlers
from litestar.datastructures import ResponseHeader
from litestar.di import Provide
from litestar.exceptions import InternalServerException
from litestar.openapi import ResponseSpec
from litestar.params import Parameter
from litestar.response import Response, Stream
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT

from gecko.api.exceptions import BadRequestException, NotFoundException
from gecko.api.routes.records import errors as e
from gecko.api.routes.records import models as m
from gecko.api.routes.records.service import Service
from gecko.api.validator import Validator
from gecko.services.records.service import RecordsService
from gecko.state import State
from gecko.utils.time import httpstringify


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(
            records=RecordsService(
                beaver=state.beaver,
                emerald=state.emerald,
            )
        )

    def build(self) -> Mapping[str, Provide]:
        """Build the dependencies."""
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the records endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        "/{event:uuid}",
        summary="List records",
    )
    async def list(  # noqa: PLR0913
        self,
        service: Service,
        event: Annotated[
            m.ListRequestEvent,
            Parameter(
                description="Identifier of the event to list records for.",
            ),
        ],
        after: Annotated[
            m.ListRequestAfter,
            Parameter(
                description="Only list records after this datetime (in event timezone).",
            ),
        ] = None,
        before: Annotated[
            m.ListRequestBefore,
            Parameter(
                description="Only list records before this datetime (in event timezone).",
            ),
        ] = None,
        limit: Annotated[
            m.ListRequestLimit,
            Parameter(
                description="Maximum number of records to return.",
            ),
        ] = 10,
        offset: Annotated[
            m.ListRequestOffset,
            Parameter(
                description="Number of records to skip.",
            ),
        ] = None,
        order: Annotated[
            m.ListRequestOrder,
            Parameter(
                description="Order to apply to the results.",
            ),
        ] = None,
    ) -> Response[m.ListResponseResults]:
        """List records."""
        req = m.ListRequest(
            event=event,
            after=after,
            before=before,
            limit=limit,
            offset=offset,
            order=order,
        )

        try:
            res = await service.list(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException from ex

        results = res.results

        return Response(results)

    @handlers.get(
        "/{event:uuid}/{start:str}",
        summary="Download record",
        response_headers=[
            ResponseHeader(
                name="Content-Type",
                description="Content type.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="Content-Length",
                description="Content length.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="ETag",
                description="Entity tag.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="Last-Modified",
                description="Last modified.",
                documentation_only=True,
            ),
        ],
        responses={
            HTTP_200_OK: ResponseSpec(
                Stream,
                description="Request fulfilled, stream follows",
                generate_examples=False,
                media_type="*/*",
            )
        },
    )
    async def download(
        self,
        service: Service,
        event: Annotated[
            m.DownloadRequestEvent,
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            str,
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
    ) -> Stream:
        """Download a record."""
        parsed_start = Validator[m.DownloadRequestStart].validate_object(start)

        req = m.DownloadRequest(
            event=event,
            start=parsed_start,
        )

        try:
            res = await service.download(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex
        except e.RecordNotFoundError as ex:
            raise NotFoundException from ex

        content_type = res.type
        size = res.size
        tag = res.tag
        modified = res.modified
        data = res.data

        headers = {
            "Content-Type": content_type,
            "Content-Length": str(size),
            "ETag": tag,
            "Last-Modified": httpstringify(modified),
        }
        return Stream(
            data,
            headers=headers,
        )

    @handlers.head(
        "/{event:uuid}/{start:str}",
        summary="Download record headers",
        response_headers=[
            ResponseHeader(
                name="Content-Type",
                description="Content type.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="Content-Length",
                description="Content length.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="ETag",
                description="Entity tag.",
                documentation_only=True,
            ),
            ResponseHeader(
                name="Last-Modified",
                description="Last modified.",
                documentation_only=True,
            ),
        ],
        responses={
            HTTP_200_OK: ResponseSpec(
                None, description="Request fulfilled, nothing follows"
            )
        },
    )
    async def headdownload(
        self,
        service: Service,
        event: Annotated[
            m.HeadDownloadRequestEvent,
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            str,
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
    ) -> Response[None]:
        """Download record headers."""
        parsed_start = Validator[m.HeadDownloadRequestStart].validate_object(start)

        req = m.HeadDownloadRequest(
            event=event,
            start=parsed_start,
        )

        try:
            res = await service.headdownload(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex
        except e.RecordNotFoundError as ex:
            raise NotFoundException from ex

        content_type = res.type
        size = res.size
        tag = res.tag
        modified = res.modified

        headers = {
            "Content-Type": content_type,
            "Content-Length": str(size),
            "ETag": tag,
            "Last-Modified": httpstringify(modified),
        }
        return Response(
            None,
            headers=headers,
        )

    @handlers.put(
        "/{event:uuid}/{start:str}",
        summary="Upload record",
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                None, description="Request fulfilled, nothing follows"
            )
        },
    )
    async def upload(
        self,
        service: Service,
        event: Annotated[
            m.UploadRequestEvent,
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            m.UploadRequestStart,
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
        content_type: Annotated[
            m.UploadRequestType,
            Parameter(
                header="Content-Type",
                description="Type of the record data.",
            ),
        ],
        request: Request,
    ) -> Response[None]:
        """Upload a record."""

        async def _stream(request: Request) -> AsyncGenerator[bytes]:
            stream = request.stream()
            while True:
                try:
                    chunk = await anext(stream)
                except (StopAsyncIteration, InternalServerException):
                    break

                yield chunk

        parsed_start = Validator[m.UploadRequestStart].validate_object(start)

        req = m.UploadRequest(
            event=event,
            start=parsed_start,
            type=content_type,
            data=_stream(request),
        )

        try:
            await service.upload(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex

        return Response(None)

    @handlers.delete(
        "/{event:uuid}/{start:str}",
        summary="Delete record",
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                None, description="Request fulfilled, nothing follows"
            )
        },
    )
    async def delete(
        self,
        service: Service,
        event: Annotated[
            m.DeleteRequestEvent,
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            str,
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
    ) -> Response[None]:
        """Delete a record."""
        parsed_start = Validator[m.DeleteRequestStart].validate_object(start)

        req = m.DeleteRequest(
            event=event,
            start=parsed_start,
        )

        try:
            await service.delete(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex
        except e.RecordNotFoundError as ex:
            raise NotFoundException from ex

        return Response(None)
