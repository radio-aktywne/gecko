from pydantic import ValidationError

from gecko.config.errors import ConfigError
from gecko.config.models import Config


class ConfigBuilder:
    """Builds the config."""

    def build(self) -> Config:
        """Build the config."""
        try:
            return Config()
        except ValidationError as ex:
            raise ConfigError from ex
