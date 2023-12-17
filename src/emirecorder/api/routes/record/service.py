from datetime import datetime, timedelta
from math import ceil
from uuid import uuid4

from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata
from pystreams.pipe import PipedStreamFactory, PipedStreamMetadata
from pystreams.s3 import S3StreamMetadata
from pystreams.srt import SRTNode
from pystreams.stream import Stream

from emirecorder.api.routes.record.models import RecordRequest, RecordResponse
from emirecorder.config.models import Config
from emirecorder.models.data import Event, RecordingCredentials
from emirecorder.time import stringify, utcnow


class Service:
    """Service for the record endpoint."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _generate_token(self) -> str:
        return uuid4().hex

    def _get_token_expiry(self) -> datetime:
        return utcnow() + timedelta(seconds=self._config.recording.timeout)

    def _create_credentials(self) -> RecordingCredentials:
        return RecordingCredentials(
            token=self._generate_token(),
            expires_at=self._get_token_expiry(),
        )

    def _build_ffmpeg_input(self, credentials: RecordingCredentials) -> FFmpegNode:
        timeout = credentials.expires_at - utcnow()
        timeout = ceil(timeout.total_seconds() * 1000000)
        timeout = max(timeout, 0)

        return SRTNode(
            host=self._config.server.host,
            port=self._config.server.port,
            options={
                "re": True,
                "mode": "listener",
                "listen_timeout": timeout,
                "passphrase": credentials.token,
            },
        )

    def _build_ffmpeg_metadata_options(self, metadata: dict[str, str]) -> list[str]:
        return [f"{key}={value}" for key, value in metadata.items()]

    def _build_ffmpeg_output(self, event: Event) -> FFmpegNode:
        return FFmpegNode(
            target="pipe:",
            options={
                "acodec": "copy",
                "f": self._config.recording.format,
                "metadata": self._build_ffmpeg_metadata_options(
                    event.show.metadata | event.metadata
                ),
            },
        )

    def _build_ffmpeg_metadata(
        self, credentials: RecordingCredentials, event: Event
    ) -> FFmpegStreamMetadata:
        return FFmpegStreamMetadata(
            input=self._build_ffmpeg_input(credentials),
            output=self._build_ffmpeg_output(event),
        )

    def _build_s3_endpoint(self) -> str:
        return f"http://{self._config.emiarchive.host}:{self._config.emiarchive.port}"

    def _build_s3_path(self, event: Event) -> str:
        start = event.start if event.start is not None else utcnow()
        filename = f"{stringify(start)}.{self._config.recording.format}"
        return f"{event.show.label}/{filename}"

    def _build_s3_metadata(self, event: Event) -> S3StreamMetadata:
        return S3StreamMetadata(
            endpoint=self._build_s3_endpoint(),
            user=self._config.emiarchive.user,
            password=self._config.emiarchive.password,
            bucket=self._config.emiarchive.bucket,
            path=self._build_s3_path(event),
        )

    def _build_stream_metadata(
        self, credentials: RecordingCredentials, event: Event
    ) -> PipedStreamMetadata:
        return PipedStreamMetadata(
            streams=[
                self._build_ffmpeg_metadata(credentials, event),
                self._build_s3_metadata(event),
            ]
        )

    async def _run_stream(self, metadata: PipedStreamMetadata) -> Stream:
        return await PipedStreamFactory().create(metadata)

    async def record(self, request: RecordRequest) -> RecordResponse:
        """Starts a recording stream and returns the credentials to access it."""

        credentials = self._create_credentials()
        metadata = self._build_stream_metadata(credentials, request.event)

        # This runs the stream in the background
        # We don't need to manage it any further
        await self._run_stream(metadata)

        return credentials
