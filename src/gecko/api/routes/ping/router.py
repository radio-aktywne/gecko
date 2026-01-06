from litestar import Router

from gecko.api.routes.ping.controller import Controller

router = Router(
    path="/ping",
    tags=["Ping"],
    route_handlers=[
        Controller,
    ],
)
