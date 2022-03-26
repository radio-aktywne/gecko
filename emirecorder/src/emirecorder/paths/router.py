from starlite import Router

from emirecorder.paths.record.router import record_router

router = Router(path="/", route_handlers=[record_router])
