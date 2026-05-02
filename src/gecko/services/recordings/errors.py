from datetime import datetime
from uuid import UUID

from gecko.utils.mime import MimeType
from gecko.utils.time import isostringify


class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class BadEventTypeError(ValidationError):
    """Raised when event type is not supported."""

    def __init__(self, event_type: str) -> None:
        super().__init__(f"Event of type {event_type} cannot be recorded.")


class EventNotFoundError(ValidationError):
    """Raised when event is not found."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(f"Live event not found for id {event_id}.")


class InstanceNotFoundError(ValidationError):
    """Raised when instance is not found."""

    def __init__(self, event_id: UUID, start: datetime) -> None:
        super().__init__(
            f"Instance not found for live event {event_id} starting at {isostringify(start)}."
        )


class UnsupportedContentTypeError(ValidationError):
    """Raised when an unsupported content type is provided."""

    def __init__(self, content_type: MimeType) -> None:
        super().__init__(f"Unsupported content type: {content_type!s}.")


class NotFoundError(ServiceError):
    """Raised when a resource is not found."""


class RecordingNotFoundError(NotFoundError):
    """Raised when recording is not found."""

    def __init__(self, event_id: UUID, start: datetime) -> None:
        super().__init__(
            f"Recording not found for instance of live event {event_id} starting at {isostringify(start)}."
        )


class BeaverError(ServiceError):
    """Raised when an beaver service operation fails."""


class EmeraldError(ServiceError):
    """Raised when a emerald database operation fails."""
