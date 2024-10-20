from datetime import datetime
from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""

    pass


class BadEventTypeError(ServiceError):
    """Raised when event type is not supported."""

    def __init__(self, type: str) -> None:
        super().__init__(f"Event of type {type} cannot be recorded.")


class EventNotFoundError(ServiceError):
    """Raised when event is not found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"Live event not found for id {event}.")


class InstanceNotFoundError(ServiceError):
    """Raised when instance is not found."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(
            f"Instance not found for live event {event} starting at {start}."
        )


class RecordNotFoundError(ServiceError):
    """Raised when record is not found."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(
            f"Record not found for instance of live event {event} starting at {start}."
        )


class BeaverError(ServiceError):
    """Raised when an beaver service operation fails."""

    pass


class EmeraldError(ServiceError):
    """Raised when a emerald database operation fails."""

    pass
