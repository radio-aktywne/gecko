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

    host: str = Field(
        "0.0.0.0",
        title="Host",
        description="Host to listen for connections on.",
    )
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
        if isinstance(v, int):
            v = {v}
        elif isinstance(v, str):
            v = set(v.split(","))

        return v


class EmiarchiveS3Config(BaseModel):
    """Configuration for the Emiarchive S3 API."""

    secure: bool = Field(
        False,
        title="Secure",
        description="Whether to use a secure connection.",
    )
    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the S3 API.",
    )
    port: int | None = Field(
        30000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the S3 API.",
    )
    user: str = Field(
        "readonly",
        title="User",
        description="Username to authenticate with the S3 API.",
    )
    password: str = Field(
        "password",
        title="Password",
        description="Password to authenticate with the S3 API.",
    )
    bucket: str = Field(
        "live",
        title="Bucket",
        description="Name of the bucket to use for uploads.",
    )

    @property
    def url(self) -> str:
        scheme = "https" if self.secure else "http"
        url = f"{scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        return url


class EmiarchiveConfig(BaseModel):
    """Configuration for the Emiarchive service."""

    s3: EmiarchiveS3Config = Field(
        EmiarchiveS3Config(),
        title="S3",
        description="Configuration for the S3 API.",
    )


class EmishowsHTTPConfig(BaseModel):
    """Configuration for the Emishows HTTP API."""

    scheme: str = Field(
        "http",
        title="Scheme",
        description="Scheme of the HTTP API.",
    )
    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the HTTP API.",
    )
    port: int | None = Field(
        35000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the HTTP API.",
    )
    path: str | None = Field(
        None,
        title="Path",
        description="Path of the HTTP API.",
    )

    @property
    def url(self) -> str:
        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmishowsConfig(BaseModel):
    """Configuration for the Emishows service."""

    http: EmishowsHTTPConfig = Field(
        EmishowsHTTPConfig(),
        title="HTTP",
        description="Configuration for the HTTP API.",
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
