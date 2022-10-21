from starlite import Router

from emirecorder.api.paths.record.router import router as record_router

router = Router(path="/", route_handlers=[record_router])
