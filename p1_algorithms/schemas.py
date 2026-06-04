from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# 基于 D'Mello & Graesser (2012) 学习情绪五分类体系
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
    # stability 是遗忘曲线 R(t)=e^(-t/S) 中的 S，随复习次数增长
    stability: float = 1.0
    # easiness_factor 是 SM-2 难度系数，初始值 2.5，下限 1.3
    easiness_factor: float = 2.5
    repetitions: int = 0
    next_review_at: datetime | None = None
    last_reviewed_at: datetime | None = None
    related_concepts: list[str] = field(default_factory=list)


@dataclass
class BehaviorSignal:
    accuracy: float
    # 答题耗时相对于本次会话均值的 z-score，由前端 30s 汇总上报
    avg_time_zscore: float
    unfocus_count: int
    pause_duration: float  # 秒


@dataclass
class SAMScore:
    # 基于 Russell (1980) 情绪环形模型的二维自报告量表
    valence: float  # 0~10, 效价轴（坏→好）
    arousal: float  # 0~10, 唤醒轴（困倦→清醒）


@dataclass
class CameraScore:
    # 由前端 face-api.js 采集，camera=None 时算法自动重新归一化权重
    focus_score: float  # 0~1, 专注度（中性表情占比）
    blink_rate: float
    head_offset: float
