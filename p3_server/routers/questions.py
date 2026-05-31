from fastapi import APIRouter, Query

from ..schemas.question import QuestionResponse, AnswerRequest, AnswerResult

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("/next", response_model=QuestionResponse)
async def get_next_question(
    chapter: int = Query(...),
    difficulty: int = Query(..., ge=1, le=3),
):
    pass


@router.post("/{question_id}/answer", response_model=AnswerResult)
async def answer_question(question_id: int, body: AnswerRequest):
    pass