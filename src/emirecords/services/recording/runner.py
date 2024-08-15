from math import ceil

from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata
from pystreams.pipe import PipedStreamFactory, PipedStreamMetadata
from pystreams.s3 import S3StreamMetadata
from pystreams.srt import SRTNode
from pystreams.stream import Stream

from emirecords.config.models import Config
from emirecords.services.emishows import models as em
from emirecords.services.recording import models as m
from emirecords.utils.time import naiveutcnow, stringify


class Runner:
    """Utility class for building and running a stream."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_ffmpeg_input(self, credentials: m.Credentials, port: int) -> FFmpegNode:
        timeout = credentials.expires_at - naiveutcnow()
        timeout = ceil(timeout.total_seconds() * 1000000)
        timeout = max(timeout, 0)

        return SRTNode(
            host=self._config.server.host,
            port=port,
            options={
                "mode": "listener",
                "listen_timeout": timeout,
                "passphrase": credentials.token,
            },
        )

    def _build_ffmpeg_output(self, format: m.Format) -> FFmpegNode:
        return FFmpegNode(
            target="pipe:",
            options={
                "acodec": "copy",
                "f": format,
            },
        )

    def _build_ffmpeg_metadata(
        self,
        credentials: m.Credentials,
        port: int,
        format: m.Format,
    ) -> FFmpegStreamMetadata:
        return FFmpegStreamMetadata(
            input=self._build_ffmpeg_input(credentials, port),
            output=self._build_ffmpeg_output(format),
        )

    def _build_s3_endpoint(self) -> str:
        return self._config.datarecords.s3.url

    def _build_s3_path(
        self,
        event: em.Event,
        instance: em.EventInstance,
        format: m.Format,
    ) -> str:
        filename = f"{stringify(instance.start)}.{format}"
        return f"{event.id}/{filename}"

    def _build_s3_metadata(
        self,
        event: em.Event,
        instance: em.EventInstance,
        format: m.Format,
    ) -> S3StreamMetadata:
        return S3StreamMetadata(
            endpoint=self._build_s3_endpoint(),
            user=self._config.datarecords.s3.user,
            password=self._config.datarecords.s3.password,
            bucket=self._config.datarecords.s3.bucket,
            path=self._build_s3_path(event, instance, format),
        )

    def _build_stream_metadata(
        self,
        event: em.Event,
        instance: em.EventInstance,
        credentials: m.Credentials,
        port: int,
        format: m.Format,
    ) -> PipedStreamMetadata:
        return PipedStreamMetadata(
            streams=[
                self._build_ffmpeg_metadata(credentials, port, format),
                self._build_s3_metadata(event, instance, format),
            ]
        )

    async def _run_stream(self, metadata: PipedStreamMetadata) -> Stream:
        return await PipedStreamFactory().create(metadata)

    async def run(
        self,
        event: em.Event,
        instance: em.EventInstance,
        credentials: m.Credentials,
        port: int,
        format: m.Format,
    ) -> Stream:
        """Run the stream."""

        metadata = self._build_stream_metadata(
            event, instance, credentials, port, format
        )
        return await self._run_stream(metadata)
