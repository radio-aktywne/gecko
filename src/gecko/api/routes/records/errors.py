class ServiceError(Exception):
    """Base class for service errors."""


class BadEventTypeError(ServiceError):
    """Raised when event type is not supported."""


class EventNotFoundError(ServiceError):
    """Raised when event is not found."""


class InstanceNotFoundError(ServiceError):
    """Raised when instance is not found."""


class RecordNotFoundError(ServiceError):
    """Raised when record is not found."""


class BeaverError(ServiceError):
    """Raised when an beaver service error occurs."""


class EmeraldError(ServiceError):
    """Raised when a emerald database error occurs."""
