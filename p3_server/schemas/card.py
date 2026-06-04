from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class CardResponse(BaseModel):
    id: int
    concept: str
    front: str
    back: str
    chapter: int
    difficulty: int = Field(ge=1, le=3, description="1基础/2理解/3应用")
    memory_strength: float = Field(ge=0.0, le=1.0)
    stability: float = Field(ge=0.0)
    repetitions: int = Field(ge=0)
    next_review_at: datetime
    last_reviewed_at: Optional[datetime] = None
    related_concepts: Optional[list[str]] = None


class ReviewRequest(BaseModel):
    quality: int = Field(ge=0, le=5, description="用户对掌握程度的评分 0-5")
    session_id: int


class ReviewResponse(BaseModel):
    next_review_at: datetime
    new_memory_strength: float = Field(ge=0.0, le=1.0)
    interval_days: int


class CurvePoint(BaseModel):
    day: int
    strength: float = Field(ge=0.0, le=1.0)


class ChapterCurve(BaseModel):
    chapter: int
    points: list[CurvePoint]


class CurveResponse(BaseModel):
    curves: list[ChapterCurve]