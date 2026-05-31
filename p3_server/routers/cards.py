from fastapi import APIRouter, Query

from ..schemas.card import CardResponse, ReviewRequest, ReviewResponse, CurveResponse

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.get("/next", response_model=CardResponse)
async def get_next_card(chapter: int | None = Query(None)):
    pass


@router.post("/{card_id}/review", response_model=ReviewResponse)
async def review_card(card_id: int, body: ReviewRequest):
    pass


@router.get("/curve", response_model=CurveResponse)
async def get_curve():
    pass