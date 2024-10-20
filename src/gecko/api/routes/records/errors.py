class ServiceError(Exception):
    """Base class for service errors."""

    pass


class BadEventTypeError(ServiceError):
    """Raised when event type is not supported."""

    pass


class EventNotFoundError(ServiceError):
    """Raised when event is not found."""

    pass


class InstanceNotFoundError(ServiceError):
    """Raised when instance is not found."""

    pass


class RecordNotFoundError(ServiceError):
    """Raised when record is not found."""

    pass


class BeaverError(ServiceError):
    """Raised when an beaver service error occurs."""

    pass


class EmeraldError(ServiceError):
    """Raised when a emerald database error occurs."""

    pass
