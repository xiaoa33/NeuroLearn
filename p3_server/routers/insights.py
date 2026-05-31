from fastapi import APIRouter

from ..schemas.dashboard import InsightResponse

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/suggestion", response_model=InsightResponse)
async def get_suggestion():
    pass