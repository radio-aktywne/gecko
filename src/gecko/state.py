from litestar.datastructures import State as LitestarState

from gecko.config.models import Config
from gecko.services.beaver.service import BeaverService
from gecko.services.emerald.service import EmeraldService


class State(LitestarState):
    """Use this class as a type hint for the state of the service."""

    beaver: BeaverService
    """Service for beaver service."""

    config: Config
    """Configuration for the service."""

    emerald: EmeraldService
    """Service for emerald database."""
