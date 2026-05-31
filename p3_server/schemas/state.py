from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class StateEnum(str, Enum):
    flow = "flow"
    anxiety = "anxiety"
    boredom = "boredom"
    confusion = "confusion"
    fatigue = "fatigue"


class BehaviorSignal(BaseModel):
    correct_rate: float = Field(ge=0.0, le=1.0)
    avg_time_zscore: Optional[float] = Field(default=None, description="答题时间 z-score")
    unfocus_count: int = Field(ge=0, default=0, description="页面失焦次数")


class SAMScore(BaseModel):
    valence: float = Field(ge=0.0, le=10.0, description="效价轴 0差-10好")
    arousal: float = Field(ge=0.0, le=10.0, description="唤醒轴 0困倦-10清醒")


class CameraScore(BaseModel):
    attention: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="专注度")
    blink_rate: Optional[float] = Field(default=None, ge=0.0)


class StateReportRequest(BaseModel):
    behavior: BehaviorSignal
    sam: SAMScore
    camera: Optional[CameraScore] = None
    session_id: int


class StateReportResponse(BaseModel):
    state: StateEnum
    score: float = Field(ge=0.0, le=1.0)
    weights: dict[str, float]
    suggestion_text: str


class StateRecord(BaseModel):
    date: str
    session_id: int
    state: StateEnum
    sam_valence: Optional[float] = None
    sam_arousal: Optional[float] = None
    cards_reviewed: int = 0
    questions_answered: int = 0


class StateHistoryResponse(BaseModel):
    records: list[StateRecord]