class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class NotFoundError(ServiceError):
    """Raised when a resource is not found."""


class BeaverError(ServiceError):
    """Raised when an beaver service error occurs."""


class EmeraldError(ServiceError):
    """Raised when a emerald database error occurs."""
