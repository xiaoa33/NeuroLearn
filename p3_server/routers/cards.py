from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from ..schemas.card import CardResponse, ReviewRequest, ReviewResponse, CurveResponse
from ..services.card_service import get_next_card, review_card_service, get_curves, get_review_queue

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.get("/next", response_model=CardResponse)
async def get_next_card_route(chapter: Optional[int] = Query(None), mode: Optional[str] = Query(None)):
    """获取下一张卡片。mode: learn=新卡, review=已学到期卡, 不传=原行为"""
    card_data = get_next_card(chapter, mode)
    if not card_data:
        raise HTTPException(status_code=404, detail="没有找到需要复习的卡片")
    
    return CardResponse(
        id=card_data["id"],
        concept=card_data["concept"],
        front=card_data["front"],
        back=card_data["back"],
        chapter=card_data["chapter"],
        difficulty=card_data["difficulty"],
        memory_strength=card_data["memory_strength"],
        stability=card_data["stability"],
        repetitions=card_data["repetitions"],
        next_review_at=card_data["next_review_at"],
        last_reviewed_at=card_data.get("last_reviewed_at"),
        related_concepts=card_data.get("related_concepts")
    )


@router.post("/{card_id}/review", response_model=ReviewResponse)
async def review_card_route(card_id: int, body: ReviewRequest):
    """
    提交卡片复习结果
    
    Args:
        card_id: 卡片ID
        body: 复习评分和会话ID
    
    Returns:
        新的记忆参数
    """
    result = review_card_service(card_id, body.quality, body.session_id)
    if not result:
        raise HTTPException(status_code=404, detail="卡片不存在")
    
    return ReviewResponse(
        next_review_at=result["next_review_at"],
        new_memory_strength=result["new_memory_strength"],
        interval_days=result["interval_days"]
    )


@router.get("/review-queue", response_model=list[CardResponse])
async def get_review_queue_route(limit: int = Query(50, ge=1, le=200), chapter: Optional[int] = Query(None)):
    """返回已学习且到期的待复习卡片，按章节可筛选。"""
    cards = get_review_queue(limit, chapter)
    return [
        CardResponse(
            id=c["id"],
            concept=c["concept"],
            front=c["front"],
            back=c["back"],
            chapter=c["chapter"],
            difficulty=c["difficulty"],
            memory_strength=c["memory_strength"],
            stability=c["stability"],
            repetitions=c["repetitions"],
            next_review_at=c["next_review_at"],
            last_reviewed_at=c.get("last_reviewed_at"),
            related_concepts=c.get("related_concepts"),
        )
        for c in cards
    ]


@router.get("/curve", response_model=CurveResponse)
async def get_curve_route():
    """
    获取所有章节的遗忘曲线
    
    Returns:
        各章节的曲线数据
    """
    result = get_curves()
    return CurveResponse(**result)
