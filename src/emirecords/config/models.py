from datetime import timedelta
from typing import Annotated, Any

from pydantic import BaseModel, Field, field_validator

from emirecords.config.base import BaseConfig


class ServerPortsConfig(BaseModel):
    """Configuration for the server ports."""

    http: int = Field(31000, ge=1, le=65535)
    """Port to listen for HTTP requests on."""

    srt: set[Annotated[int, Field(..., ge=1, le=65535)]] = Field({31000}, min_length=1)
    """Ports to select from when listening for SRT connections."""

    @field_validator("srt", mode="before")
    @classmethod
    def validate_srt(cls, v: Any) -> Any:
        if isinstance(v, int):
            v = {v}
        elif isinstance(v, str):
            v = set(v.split(","))

        return v


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = "0.0.0.0"
    """Host to run the server on."""

    ports: ServerPortsConfig = ServerPortsConfig()
    """Configuration for the server ports."""

    trusted: str | list[str] | None = "*"
    """Trusted IP addresses."""


class RecordingConfig(BaseModel):
    """Configuration for the recording service."""

    timeout: timedelta = Field(timedelta(minutes=1), ge=0)
    """Time after which a stream will be stopped if no connections are made."""

    window: timedelta = timedelta(hours=1)
    """Time window to search for event instances around the current time."""


class DatarecordsS3Config(BaseModel):
    """Configuration for the S3 API of the datarecords database."""

    secure: bool = False
    """Whether to use a secure connection."""

    host: str = "localhost"
    """Host of the S3 API."""

    port: int | None = Field(30000, ge=1, le=65535)
    """Port of the S3 API."""

    user: str = "readonly"
    """Username to authenticate with the S3 API."""

    password: str = "password"
    """Password to authenticate with the S3 API."""

    bucket: str = "live"
    """Name of the bucket to use for uploads."""

    @property
    def url(self) -> str:
        """URL of the S3 API."""

        scheme = "https" if self.secure else "http"
        url = f"{scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        return url


class DatarecordsConfig(BaseModel):
    """Configuration for the datarecords database."""

    s3: DatarecordsS3Config = DatarecordsS3Config()
    """Configuration for the S3 API of the datarecords database."""


class EmishowsHTTPConfig(BaseModel):
    """Configuration for the HTTP API of the emishows service."""

    scheme: str = "http"
    """Scheme of the HTTP API."""

    host: str = "localhost"
    """Host of the HTTP API."""

    port: int | None = Field(35000, ge=1, le=65535)
    """Port of the HTTP API."""

    path: str | None = None
    """Path of the HTTP API."""

    @property
    def url(self) -> str:
        """URL of the HTTP API."""

        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmishowsConfig(BaseModel):
    """Configuration for the emishows service."""

    http: EmishowsHTTPConfig = EmishowsHTTPConfig()
    """Configuration for the HTTP API of the emishows service."""


class Config(BaseConfig):
    """Configuration for the application."""

    server: ServerConfig = ServerConfig()
    """Configuration for the server."""

    recording: RecordingConfig = RecordingConfig()
    """Configuration for the recording service."""

    datarecords: DatarecordsConfig = DatarecordsConfig()
    """Configuration for the datarecords database."""

    emishows: EmishowsConfig = EmishowsConfig()
    """Configuration for the emishows service."""

    debug: bool = False
    """Enable debug mode."""
