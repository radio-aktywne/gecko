from litestar.datastructures import State as LitestarState

from emirecords.config.models import Config
from emirecords.services.emishows.service import EmishowsService
from emirecords.services.recording.service import RecordingService


class State(LitestarState):
    """Use this class as a type hint for the state of the application."""

    config: Config
    """Configuration for the application."""

    emishows: EmishowsService
    """Service for emishows API."""

    recording: RecordingService
    """Service to manage recording."""
