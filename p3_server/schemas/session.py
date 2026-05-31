from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionStartResponse(BaseModel):
    session_id: int
    started_at: datetime


class SessionEndRequest(BaseModel):
    final_state: Optional[str] = None
    sam_valence: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    sam_arousal: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    cards_reviewed: int = Field(default=0, ge=0)
    questions_answered: int = Field(default=0, ge=0)


class SessionEndResponse(BaseModel):
    session_id: int
    ended_at: datetime
    duration_minutes: float