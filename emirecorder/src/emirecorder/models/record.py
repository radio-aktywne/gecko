from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    id: str
    title: str
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class Token(BaseModel):
    token: str
    expires_at: datetime


class RecordRequest(BaseModel):
    event: Event


class RecordResponse(BaseModel):
    token: Token
