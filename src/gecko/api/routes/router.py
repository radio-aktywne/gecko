from litestar import Router

from gecko.api.routes.ping.router import router as ping
from gecko.api.routes.records.router import router as records
from gecko.api.routes.sse.router import router as sse
from gecko.api.routes.test.router import router as test

router = Router(
    path="/",
    route_handlers=[
        ping,
        records,
        sse,
        test,
    ],
)
