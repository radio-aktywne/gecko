from starlite import Router

from emirecorder.api.paths.record.controller import RecordController

router = Router(path="/record", route_handlers=[RecordController])
