from datetime import datetime
from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""

    pass


class EventNotFoundError(ServiceError):
    """Raised when event is not found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"Event not found for id {event}.")


class InstanceNotFoundError(ServiceError):
    """Raised when instance is not found."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(f"Instance not found for event {event} starting at {start}.")


class RecordNotFoundError(ServiceError):
    """Raised when record is not found."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(
            f"Record not found for instance of event {event} starting at {start}."
        )


class RecordAlreadyExistsError(ServiceError):
    """Raised when record already exists."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(
            f"Record already exists for instance of event {event} starting at {start}."
        )


class EmishowsError(ServiceError):
    """Raised when an emishows service error occurs."""

    pass


class MediarecordsError(ServiceError):
    """Raised when a mediarecords database error occurs."""

    pass
