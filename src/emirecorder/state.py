from litestar.datastructures import State as LitestarState

from emirecorder.config.models import Config
from emirecorder.emishows.service import EmishowsService
from emirecorder.recording.recorder import Recorder


class State(LitestarState):
    """Use this class as a type hint for the state of your application.

    Attributes:
        config: Configuration for the application.
        emishows: Service for emishows API.
        recorder: Recorder for managing recordings.
    """

    config: Config
    emishows: EmishowsService
    recorder: Recorder
