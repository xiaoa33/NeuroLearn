from fastapi import APIRouter

from ..schemas.dashboard import InsightResponse
from ..services.insight_service import get_insight_suggestion

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/suggestion", response_model=InsightResponse)
async def get_suggestion_route():
    """
    获取学习洞察建议（模拟数据）
    
    Returns:
        即时建议和今日计划建议
    """
    suggestion = get_insight_suggestion()
    return InsightResponse(
        instant_advice=suggestion["instant_advice"],
        today_plan=suggestion["today_plan"]
    )
