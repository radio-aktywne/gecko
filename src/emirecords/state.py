from litestar.datastructures import State as LitestarState

from emirecords.config.models import Config
from emirecords.services.emishows.service import EmishowsService
from emirecords.services.mediarecords.service import MediarecordsService


class State(LitestarState):
    """Use this class as a type hint for the state of the application."""

    config: Config
    """Configuration for the application."""

    emishows: EmishowsService
    """Service for emishows API."""

    mediarecords: MediarecordsService
    """Service for mediarecords database."""
