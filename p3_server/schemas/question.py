from typing import Optional

from pydantic import BaseModel, Field


class QuestionResponse(BaseModel):
    id: int
    chapter: int
    stem: str
    options: Optional[list[str]] = None
    type: str = Field(default="choice", description="choice / truefalse / fill")
    difficulty: int = Field(ge=1, le=3, description="1简单/2中等/3困难")
    related_card_id: Optional[int] = None


class AnswerRequest(BaseModel):
    answer: str
    time_ms: int = Field(ge=0, description="答题耗时（毫秒）")
    session_id: int


class AnswerResult(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    next_difficulty: int = Field(ge=1, le=3, description="推荐的下一题难度")
    reason: Optional[str] = Field(default=None, description="难度调整原因")