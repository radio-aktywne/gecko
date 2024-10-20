from litestar import Router

from gecko.api.routes.ping.router import router as ping_router
from gecko.api.routes.records.router import router as records_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        records_router,
    ],
)
