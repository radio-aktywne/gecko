from litestar import Router

from emirecords.api.routes.ping.router import router as ping_router
from emirecords.api.routes.record.router import router as record_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        record_router,
    ],
)
