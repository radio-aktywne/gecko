from litestar import Router

from emirecorder.api.routes.record.router import router as record_router

router = Router(
    path="/",
    route_handlers=[
        record_router,
    ],
)
