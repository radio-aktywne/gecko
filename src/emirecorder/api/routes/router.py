from litestar import Router

from emirecorder.api.routes.ping.router import router as ping_router
from emirecorder.api.routes.record.router import router as record_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        record_router,
    ],
)
