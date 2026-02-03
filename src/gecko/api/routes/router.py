from litestar import Router

from gecko.api.routes.ping.router import router as ping_router
from gecko.api.routes.records.router import router as records_router
from gecko.api.routes.sse.router import router as sse_router
from gecko.api.routes.test.router import router as test_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        records_router,
        sse_router,
        test_router,
    ],
)
