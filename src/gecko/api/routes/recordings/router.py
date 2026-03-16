from litestar import Router

from gecko.api.routes.recordings.controller import Controller

router = Router(
    path="/recordings",
    tags=["Recordings"],
    route_handlers=[
        Controller,
    ],
)
