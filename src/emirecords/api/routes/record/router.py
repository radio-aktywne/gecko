from litestar import Router

from emirecords.api.routes.record.controller import Controller

router = Router(
    path="/record",
    route_handlers=[
        Controller,
    ],
)
