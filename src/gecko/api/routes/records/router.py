from litestar import Router

from gecko.api.routes.records.controller import Controller

router = Router(
    path="/records",
    route_handlers=[
        Controller,
    ],
)
