from emirecorder.models.data import Event, Token
from emirecorder.models.base import SerializableModel


class RecordRequest(SerializableModel):
    event: Event


class RecordResponse(SerializableModel):
    token: Token
