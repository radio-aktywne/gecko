from collections.abc import AsyncGenerator, Mapping
from dataclasses import dataclass
from typing import Annotated, cast

from litestar import Controller as BaseController
from litestar import Request, handlers
from litestar.datastructures import ResponseHeader
from litestar.di import Provide
from litestar.exceptions import InternalServerException
from litestar.openapi.spec import (
    OpenAPIFormat,
    OpenAPIMediaType,
    OpenAPIResponse,
    OpenAPIType,
    Operation,
    RequestBody,
    Schema,
)
from litestar.params import Parameter
from litestar.response import Response, Stream
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT

from gecko.api.exceptions import BadRequestException, NotFoundException
from gecko.api.routes.records import errors as e
from gecko.api.routes.records import models as m
from gecko.api.routes.records.service import Service
from gecko.models.base import Jsonable, Serializable
from gecko.services.records.service import RecordsService
from gecko.state import State
from gecko.utils.time import httpstringify


@dataclass
class DownloadOperation(Operation):
    """OpenAPI Operation for downloading a record."""

    def __post_init__(self) -> None:
        if (
            self.responses
            and str(HTTP_200_OK) in self.responses
            and (response := self.responses[str(HTTP_200_OK)])
            and isinstance(response, OpenAPIResponse)
            and (content := response.content)
            and "*/*" in content
            and (schema := content["*/*"].schema)
            and isinstance(schema, Schema)
        ):
            schema.type = OpenAPIType.STRING
            schema.format = OpenAPIFormat.BINARY


@dataclass
class UploadOperation(Operation):
    """OpenAPI Operation for uploading a record."""

    def __post_init__(self) -> None:
        self.request_body = RequestBody(
            content={
                "*/*": OpenAPIMediaType(
                    schema=Schema(type=OpenAPIType.STRING, format=OpenAPIFormat.BINARY)
                )
            },
            required=True,
        )


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(
            records=RecordsService(beaver=state.beaver, emerald=state.emerald)
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
        "/{event:str}",
        summary="List records",
        raises=[BadRequestException, NotFoundException],
    )
    async def list(  # noqa: PLR0913
        self,
        service: Service,
        event: Annotated[
            Serializable[m.ListRequestEvent],
            Parameter(
                description="Identifier of the event to list records for.",
            ),
        ],
        after: Annotated[
            Jsonable[m.ListRequestAfter] | None,
            Parameter(
                description="Only list records after this datetime (in event timezone).",
            ),
        ] = None,
        before: Annotated[
            Jsonable[m.ListRequestBefore] | None,
            Parameter(
                description="Only list records before this datetime (in event timezone).",
            ),
        ] = None,
        limit: Annotated[
            Jsonable[m.ListRequestLimit] | None,
            Parameter(
                description="Maximum number of records to return. Default is 10.",
            ),
        ] = None,
        offset: Annotated[
            Jsonable[m.ListRequestOffset] | None,
            Parameter(
                description="Number of records to skip.",
            ),
        ] = None,
        order: Annotated[
            Jsonable[m.ListRequestOrder] | None,
            Parameter(
                description="Order to apply to the results.",
            ),
        ] = None,
    ) -> Response[Serializable[m.ListResponseResults]]:
        """List records."""
        request = m.ListRequest(
            event=event.root,
            after=after.root if after else None,
            before=before.root if before else None,
            limit=limit.root if limit else 10,
            offset=offset.root if offset else None,
            order=order.root if order else None,
        )

        try:
            response = await service.list(request)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.results))

    @handlers.get(
        "/{event:str}/{start:str}",
        summary="Download record",
        status_code=HTTP_200_OK,
        response_headers=[
            ResponseHeader(
                name="Content-Type",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="Content-Length",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="ETag",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="Last-Modified",
                required=True,
                documentation_only=True,
            ),
        ],
        media_type="*/*",
        raises=[BadRequestException, NotFoundException],
        operation_class=DownloadOperation,
    )
    async def download(
        self,
        service: Service,
        event: Annotated[
            Serializable[m.DownloadRequestEvent],
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            Serializable[m.DownloadRequestStart],
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
    ) -> Stream:
        """Download a record."""
        request = m.DownloadRequest(event=event.root, start=start.root)

        try:
            response = await service.download(request)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex
        except e.RecordNotFoundError as ex:
            raise NotFoundException from ex

        return Stream(
            response.data,
            headers={
                "Content-Type": response.type,
                "Content-Length": str(response.size),
                "ETag": response.tag,
                "Last-Modified": httpstringify(response.modified),
            },
        )

    @handlers.head(
        "/{event:str}/{start:str}",
        summary="Download record headers",
        response_description="Request fulfilled, headers follow",
        response_headers=[
            ResponseHeader(
                name="Content-Type",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="Content-Length",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="ETag",
                required=True,
                documentation_only=True,
            ),
            ResponseHeader(
                name="Last-Modified",
                required=True,
                documentation_only=True,
            ),
        ],
        raises=[BadRequestException, NotFoundException],
    )
    async def headdownload(
        self,
        service: Service,
        event: Annotated[
            Serializable[m.HeadDownloadRequestEvent],
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            Serializable[m.HeadDownloadRequestStart],
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
    ) -> None:
        """Download record headers."""
        request = m.HeadDownloadRequest(event=event.root, start=start.root)

        try:
            response = await service.headdownload(request)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex
        except e.RecordNotFoundError as ex:
            raise NotFoundException from ex

        return cast(
            "None",
            Response(
                None,
                headers={
                    "Content-Type": response.type,
                    "Content-Length": str(response.size),
                    "ETag": response.tag,
                    "Last-Modified": httpstringify(response.modified),
                },
            ),
        )

    @handlers.put(
        "/{event:str}/{start:str}",
        summary="Upload record",
        status_code=HTTP_204_NO_CONTENT,
        raises=[BadRequestException, NotFoundException],
        operation_class=UploadOperation,
    )
    async def upload(
        self,
        service: Service,
        event: Annotated[
            Serializable[m.UploadRequestEvent],
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            Serializable[m.UploadRequestStart],
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
        content_type: Annotated[
            Jsonable[m.UploadRequestType],
            Parameter(
                header="Content-Type",
                description="Type of the record data.",
            ),
        ],
        request: Request,
    ) -> None:
        """Upload a record."""

        async def _stream(request: Request) -> AsyncGenerator[bytes]:
            stream = request.stream()
            while True:
                try:
                    chunk = await anext(stream)
                except (StopAsyncIteration, InternalServerException):
                    break

                yield chunk

        req = m.UploadRequest(
            event=event.root,
            start=start.root,
            type=content_type.root,
            data=_stream(request),
        )

        try:
            await service.upload(req)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex

    @handlers.delete(
        "/{event:str}/{start:str}",
        summary="Delete record",
        raises=[BadRequestException, NotFoundException],
    )
    async def delete(
        self,
        service: Service,
        event: Annotated[
            Serializable[m.DeleteRequestEvent],
            Parameter(
                description="Identifier of the event.",
            ),
        ],
        start: Annotated[
            Serializable[m.DeleteRequestStart],
            Parameter(
                description="Start datetime of the event instance in event timezone.",
            ),
        ],
    ) -> None:
        """Delete a record."""
        request = m.DeleteRequest(event=event.root, start=start.root)

        try:
            await service.delete(request)
        except e.BadEventTypeError as ex:
            raise BadRequestException from ex
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex
        except e.RecordNotFoundError as ex:
            raise NotFoundException from ex
