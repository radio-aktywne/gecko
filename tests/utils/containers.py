import asyncio

from testcontainers.core.container import DockerContainer


class AsyncDockerContainer(DockerContainer):
    """DockerContainer with async methods."""

    async def __aenter__(self):
        return await asyncio.to_thread(self.__enter__)

    async def __aexit__(self, *args, **kwargs):
        return await asyncio.to_thread(self.__exit__, *args, **kwargs)

    async def aexec(self, *args, **kwargs):
        return await asyncio.to_thread(self.exec, *args, **kwargs)


class ContainerNotReadyError(Exception):
    """Container is not ready."""

    def __init__(self, output: bytes) -> None:
        super().__init__(f"Container is not ready. Output: {output.decode()}")


class ContainerWaiter:
    """Wait for container to be ready using a command."""

    def __init__(
        self,
        container: AsyncDockerContainer,
        command: str | list[str],
        tries: int = 10,
        timeout: int = 1,
    ) -> None:
        self._container = container
        self._command = command
        self._tries = tries
        self._timeout = timeout

    async def wait(self) -> None:
        """Wait for container to be ready."""

        i = 0
        while True:
            code, output = await self._container.aexec(self._command)
            if code == 0:
                break
            if i > self._tries:
                raise ContainerNotReadyError(output)
            await asyncio.sleep(self._timeout)
            i += 1
