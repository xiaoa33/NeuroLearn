from typing import Optional

from pydantic import BaseModel, Field

from .state import StateEnum


class DashboardSummary(BaseModel):
    due_cards_today: int = Field(description="今日到期卡片数")
    streak_days: int = Field(description="连续学习天数")
    overall_memory_strength: float = Field(ge=0.0, le=1.0, description="整体记忆强度")
    chapter_strengths: dict[int, float] = Field(description="各章节平均记忆强度")
    recent_states: list[dict] = Field(default_factory=list, description="最近状态记录")
    total_cards: int = 0
    total_questions_answered: int = 0


class InsightResponse(BaseModel):
    instant_advice: str = Field(description="即时建议（1条）")
    today_plan: str = Field(description="今日计划建议（1条）")