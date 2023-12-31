class ServiceError(Exception):
    """Base class for service errors."""

    def __init__(self, message: str | None = None) -> None:
        self._message = message

        args = (message,) if message else ()
        super().__init__(*args)

    @property
    def message(self) -> str | None:
        return self._message


class InstanceNotFoundError(ServiceError):
    """Raised when an event instance is not found."""

    pass


class RecorderBusyError(ServiceError):
    """Raised when the recorder is busy."""

    pass
