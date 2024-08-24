from litestar import Router

from emirecords.api.routes.records.controller import Controller

router = Router(
    path="/records",
    route_handlers=[
        Controller,
    ],
)
