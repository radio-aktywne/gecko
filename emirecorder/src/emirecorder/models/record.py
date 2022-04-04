from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class Show(BaseModel):
    label: str
    metadata: Dict[str, str] = {}


class Event(BaseModel):
    show: Show
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    metadata: Dict[str, str] = {}


class Token(BaseModel):
    token: str
    expires_at: datetime


class RecordRequest(BaseModel):
    event: Event


class RecordResponse(BaseModel):
    token: Token
