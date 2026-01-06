from litestar import Router

from gecko.api.routes.records.controller import Controller

router = Router(
    path="/records",
    tags=["Records"],
    route_handlers=[
        Controller,
    ],
)
