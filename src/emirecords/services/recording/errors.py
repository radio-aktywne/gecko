from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""

    pass


class InstanceNotFoundError(ServiceError):
    """Raised when no near instances of an event are found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"No near instances of event {event} found.")


class NoPortsAvailableError(ServiceError):
    """Raised when no ports are available."""

    def __init__(self) -> None:
        super().__init__("No ports available.")


class EmishowsError(ServiceError):
    """Raised when an emishows service operation fails."""

    pass
