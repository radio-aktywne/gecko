from pydantic import BaseModel, Field

from emirecorder.config.base import BaseConfig


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = Field(
        "0.0.0.0",
        title="Host",
        description="Host to run the server on.",
    )
    port: int = Field(
        31000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to run the server on.",
    )


class RecordingConfig(BaseModel):
    """Configuration for the recording process."""

    timeout: int = Field(
        60,
        ge=0,
        title="Timeout",
        description="Number of seconds to wait for a connection.",
    )
    format: str = Field(
        "ogg",
        title="Format",
        description="Format to record in.",
    )


class EmiarchiveConfig(BaseModel):
    """Configuration for the Emiarchive service."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host to connect to.",
    )
    port: int = Field(
        30000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to connect to.",
    )
    user: str = Field(
        "readwrite",
        title="User",
        description="Username to connect with.",
    )
    password: str = Field(
        "password",
        title="Password",
        description="Password to connect with.",
    )
    bucket: str = Field(
        "live",
        title="Bucket",
        description="Name of the bucket to use for uploads.",
    )


class Config(BaseConfig):
    """Configuration for the application."""

    server: ServerConfig = Field(
        ServerConfig(),
        title="Server",
        description="Configuration for the server.",
    )
    recording: RecordingConfig = Field(
        RecordingConfig(),
        title="Recording",
        description="Configuration for the recording process.",
    )
    emiarchive: EmiarchiveConfig = Field(
        EmiarchiveConfig(),
        title="Emiarchive",
        description="Configuration for the Emiarchive service.",
    )
