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


class RecordAlreadyExistsError(ServiceError):
    """Raised when record already exists."""

    pass


class EmishowsError(ServiceError):
    """Raised when an emishows service error occurs."""

    pass


class MediarecordsError(ServiceError):
    """Raised when a mediarecords database error occurs."""

    pass
