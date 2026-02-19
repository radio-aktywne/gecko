from typing import Literal

from pydantic import Field

from gecko.models.base import SerializableModel
from gecko.models.events.enums import EventType
from gecko.models.events.fields import CreatedAtField, DataField, TypeField
from gecko.utils.time import naiveutcnow


class TestEventData(SerializableModel):
    """Data of a test event."""

    message: str
    """Message of the test event."""


class TestEvent(SerializableModel):
    """Event that is emitted for testing purposes."""

    type: TypeField[Literal[EventType.TEST]] = EventType.TEST
    created_at: CreatedAtField = Field(default_factory=naiveutcnow)
    data: DataField[TestEventData]
