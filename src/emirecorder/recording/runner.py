from math import ceil

from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata
from pystreams.pipe import PipedStreamFactory, PipedStreamMetadata
from pystreams.s3 import S3StreamMetadata
from pystreams.srt import SRTNode
from pystreams.stream import Stream

from emirecorder.config.models import Config
from emirecorder.emishows.models import Event, EventInstance
from emirecorder.recording.models import Credentials, Format
from emirecorder.time import naiveutcnow, stringify


class StreamRunner:
    """Utility class for building and running a stream."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_ffmpeg_input(self, credentials: Credentials, port: int) -> FFmpegNode:
        """Builds an FFmpeg input node."""

        timeout = credentials.expires_at - naiveutcnow()
        timeout = ceil(timeout.total_seconds() * 1000000)
        timeout = max(timeout, 0)

        return SRTNode(
            host=self._config.recorder.host,
            port=port,
            options={
                "mode": "listener",
                "listen_timeout": timeout,
                "passphrase": credentials.token,
            },
        )

    def _build_ffmpeg_output(self, format: Format) -> FFmpegNode:
        """Builds an FFmpeg output node."""

        return FFmpegNode(
            target="pipe:",
            options={"acodec": "copy", "f": format},
        )

    def _build_ffmpeg_metadata(
        self,
        credentials: Credentials,
        port: int,
        format: Format,
    ) -> FFmpegStreamMetadata:
        """Builds FFmpeg stream metadata."""

        return FFmpegStreamMetadata(
            input=self._build_ffmpeg_input(credentials, port),
            output=self._build_ffmpeg_output(format),
        )

    def _build_s3_endpoint(self) -> str:
        """Builds an S3 endpoint URL."""

        return self._config.emiarchive.s3.url

    def _build_s3_path(
        self,
        event: Event,
        instance: EventInstance,
        format: Format,
    ) -> str:
        """Builds an S3 path for the target file."""

        filename = f"{stringify(instance.start)}.{format}"
        return f"{event.id}/{filename}"

    def _build_s3_metadata(
        self,
        event: Event,
        instance: EventInstance,
        format: Format,
    ) -> S3StreamMetadata:
        """Builds S3 stream metadata."""

        return S3StreamMetadata(
            endpoint=self._build_s3_endpoint(),
            user=self._config.emiarchive.s3.user,
            password=self._config.emiarchive.s3.password,
            bucket=self._config.emiarchive.s3.bucket,
            path=self._build_s3_path(event, instance, format),
        )

    def _build_stream_metadata(
        self,
        event: Event,
        instance: EventInstance,
        credentials: Credentials,
        port: int,
        format: Format,
    ) -> PipedStreamMetadata:
        """Builds stream metadata."""

        return PipedStreamMetadata(
            streams=[
                self._build_ffmpeg_metadata(credentials, port, format),
                self._build_s3_metadata(event, instance, format),
            ]
        )

    async def _run_stream(self, metadata: PipedStreamMetadata) -> Stream:
        """Run the stream with the given metadata."""

        return await PipedStreamFactory().create(metadata)

    async def run(
        self,
        event: Event,
        instance: EventInstance,
        credentials: Credentials,
        port: int,
        format: Format,
    ) -> Stream:
        """Run the stream."""

        metadata = self._build_stream_metadata(
            event, instance, credentials, port, format
        )
        return await self._run_stream(metadata)
