from fastapi import APIRouter

from ..schemas.dashboard import DashboardSummary
from p2_knowledge.db_service import get_dashboard_summary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary_route():
    """返回仪表盘汇总数据：今日到期卡片数、连续天数、各章节记忆强度。"""
    data = get_dashboard_summary()
    return DashboardSummary(
        due_cards_today=data["due_cards_today"],
        streak_days=data["streak_days"],
        chapter_strengths=data["chapter_strengths"],
        recent_states=data["recent_states"],
        total_cards=data["total_cards"],
        total_cards_reviewed=data["total_cards_reviewed"],
        total_questions_answered=data["total_questions_answered"],
    )
