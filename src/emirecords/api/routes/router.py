from litestar import Router

from emirecords.api.routes.ping.router import router as ping_router
from emirecords.api.routes.records.router import router as records_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        records_router,
    ],
)
