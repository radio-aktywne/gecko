from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.di import Provide
from litestar.params import Body
from litestar.response import Response

from emirecords.api.exceptions import ConflictException, UnprocessableContentException
from emirecords.api.routes.record import errors as e
from emirecords.api.routes.record import models as m
from emirecords.api.routes.record.service import Service
from emirecords.api.validator import Validator
from emirecords.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(
            recording=state.recording,
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the record endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.post(
        summary="Request a recording",
        raises=[
            ConflictException,
            UnprocessableContentException,
        ],
    )
    async def record(
        self,
        service: Service,
        data: Annotated[
            m.RecordRequestData,
            Body(
                description="Data for the request.",
            ),
        ],
    ) -> Response[m.RecordResponseData]:
        """Request a recording for a given event."""

        data = Validator(m.RecordRequestData).object(data)

        req = m.RecordRequest(
            data=data,
        )

        try:
            res = await service.record(req)
        except e.ValidationError as ex:
            raise UnprocessableContentException(extra=str(ex)) from ex
        except e.ServiceBusyError as ex:
            raise ConflictException(extra=str(ex)) from ex

        rdata = res.data

        return Response(rdata)
