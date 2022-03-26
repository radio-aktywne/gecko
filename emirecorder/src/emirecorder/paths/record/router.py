from starlite import Router

from emirecorder.paths.record.controller import RecordController

record_router = Router(path="/record", route_handlers=[RecordController])
