from datetime import timedelta
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

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


class RecorderConfig(BaseModel):
    """Configuration for the recorder."""

    ports: set[Annotated[int, Field(..., ge=1, le=65535)]] = Field(
        {31000},
        min_length=1,
        title="Ports",
        description="Ports to select from when listening for connections.",
    )
    timeout: timedelta = Field(
        timedelta(minutes=1),
        ge=0,
        title="Timeout",
        description="Time after which a stream will be stopped if no connections are made.",
    )
    window: timedelta = Field(
        timedelta(hours=1),
        title="Window",
        description="Time window to search for event instances around the current time.",
    )

    @field_validator("ports", mode="before")
    @classmethod
    def validate_ports(cls, v):
        if isinstance(v, str):
            v = set(v.split(","))
        return v


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


class EmishowsConfig(BaseModel):
    """Configuration for the Emishows service."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host to connect to.",
    )
    port: int = Field(
        35000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to connect to.",
    )


class Config(BaseConfig):
    """Configuration for the application."""

    server: ServerConfig = Field(
        ServerConfig(),
        title="Server",
        description="Configuration for the server.",
    )
    recorder: RecorderConfig = Field(
        RecorderConfig(),
        title="Recorder",
        description="Configuration for the recorder.",
    )
    emiarchive: EmiarchiveConfig = Field(
        EmiarchiveConfig(),
        title="Emiarchive",
        description="Configuration for the Emiarchive service.",
    )
    emishows: EmishowsConfig = Field(
        EmishowsConfig(),
        title="Emishows",
        description="Configuration for the Emishows service.",
    )
