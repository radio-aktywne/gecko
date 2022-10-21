import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from pystreams.ffmpeg import FFmpegNode, FFmpegStream
from pystreams.minio import MinioNode, MinioStream
from pystreams.pipe import Pipe
from pystreams.srt import SRTNode
from pystreams.stream import Stream as PyStream

from emirecorder.config import Config
from emirecorder.models.data import Token, Event
from emirecorder.time import stringify, utcnow
from emirecorder.utils import generate_uuid, background


class StreamManager:
    FORMAT = "opus"

    def __init__(self, config: Config) -> None:
        self.config = config
        self.stream = None

    def create_token(self) -> Token:
        return Token(
            token=generate_uuid(),
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=self.config.timeout),
        )

    def get_target_host(self) -> str:
        return f"http://{self.config.target_user}:{self.config.target_password}@{self.config.target_host}:{self.config.target_port}"

    def get_target_path(self, event: Event) -> str:
        start = event.start if event.start is not None else utcnow()
        filename = f"{stringify(start)}.{self.FORMAT}"
        return f"{event.show.label}/{filename}"

    @staticmethod
    def _metadata_values(metadata: Dict[str, str]) -> List[str]:
        return [f"{key}={value}" for key, value in metadata.items()]

    def create_stream(self, token: str, event: Event) -> PyStream:
        return Pipe(
            FFmpegStream(
                input=SRTNode(
                    host="0.0.0.0",
                    port=str(self.config.port),
                    options={
                        "re": None,
                        "mode": "listener",
                        "listen_timeout": int(self.config.timeout * 1000000),
                        "passphrase": token,
                    },
                ),
                output=FFmpegNode(
                    target="-",
                    options={
                        "acodec": "copy",
                        "format": self.FORMAT,
                        "metadata": self._metadata_values(
                            event.show.metadata | event.metadata
                        ),
                    },
                ),
            ),
            MinioStream(
                MinioNode(
                    host=self.get_target_host(),
                    bucket=self.config.target_bucket,
                    path=self.get_target_path(event),
                )
            ),
        )

    async def monitor(self) -> None:
        await background(self.stream.wait)
        self.stream = None

    def record(self, event: Event) -> Token:
        if self.stream is not None:
            raise RuntimeError("Stream is busy.")
        token = self.create_token()
        self.stream = self.create_stream(token.token, event)
        self.stream.start()
        asyncio.create_task(self.monitor())
        return token
