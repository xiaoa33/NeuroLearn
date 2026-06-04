from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class StateEnum(str, Enum):
    flow = "flow"
    anxiety = "anxiety"
    boredom = "boredom"
    confusion = "confusion"
    fatigue = "fatigue"


@dataclass
class CardData:
    id: int
    chapter: int
    concept: str
    front: str
    back: str
    difficulty: int = 2
    memory_strength: float = 1.0
    stability: float = 1.0
    easiness_factor: float = 2.5
    repetitions: int = 0
    next_review_at: datetime | None = None
    last_reviewed_at: datetime | None = None
    related_concepts: list[str] = field(default_factory=list)


@dataclass
class BehaviorSignal:
    accuracy: float
    avg_time_zscore: float
    unfocus_count: int
    pause_duration: float  # 秒


@dataclass
class SAMScore:
    valence: float  # 0~10, 效价轴
    arousal: float  # 0~10, 唤醒轴


@dataclass
class CameraScore:
    focus_score: float  # 0~1, 专注度
    blink_rate: float
    head_offset: float
