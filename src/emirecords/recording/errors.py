from uuid import UUID


class RecordingError(Exception):
    """Base class for all exceptions related to recording."""

    def __init__(self, message: str | None = None) -> None:
        self._message = message

        args = (message,) if message else ()
        super().__init__(*args)

    @property
    def message(self) -> str | None:
        return self._message


class InstanceNotFoundError(RecordingError):
    """Raised when no near instances of an event are found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"No near instances of event {event} found.")


class NoPortsAvailableError(RecordingError):
    """Raised when no ports are available."""

    def __init__(self) -> None:
        super().__init__("No ports available.")
