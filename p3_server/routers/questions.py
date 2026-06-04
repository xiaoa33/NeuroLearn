from fastapi import APIRouter, Query, HTTPException

from ..schemas.question import QuestionResponse, AnswerRequest, AnswerResult
from ..services.quiz_service import get_next_question, answer_question

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("/next", response_model=QuestionResponse)
async def get_next_question_route(
    chapter: int = Query(..., description="章节"),
    difficulty: int = Query(..., ge=1, le=3, description="难度 1-3"),
    session_id: int = Query(None, description="会话ID")
):
    """
    获取下一道题目
    
    Args:
        chapter: 章节
        difficulty: 难度
        session_id: 会话ID，可选
    
    Returns:
        题目数据
    """
    question_data = get_next_question(chapter, difficulty, session_id)
    if not question_data:
        raise HTTPException(status_code=404, detail="没有找到可用的题目")
    
    return QuestionResponse(
        id=question_data["id"],
        chapter=question_data["chapter"],
        stem=question_data["stem"],
        options=question_data.get("options"),
        type=question_data["type"],
        difficulty=question_data["difficulty"],
        related_card_id=question_data.get("related_card_id")
    )


@router.post("/{question_id}/answer", response_model=AnswerResult)
async def answer_question_route(question_id: int, body: AnswerRequest):
    """
    提交题目答案
    
    Args:
        question_id: 题目ID
        body: 答案、耗时和会话ID
    
    Returns:
        答题结果和下一题难度建议
    """
    result = answer_question(question_id, body.answer, body.time_ms, body.session_id, state=body.state)
    if not result:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    return AnswerResult(
        is_correct=result["is_correct"],
        correct_answer=result["correct_answer"],
        explanation=result.get("explanation"),
        next_difficulty=result["next_difficulty"],
        reason=result.get("reason")
    )
