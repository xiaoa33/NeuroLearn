from fastapi import APIRouter

from ..schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# 添加路径
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "p2_knowledge"))
from p2_knowledge.db_service import get_dashboard_summary
from p2_knowledge.db_service import SessionLocal
from p2_knowledge.models.card import Card
from p2_knowledge.models.response import QuestionResponse as DbQuestionResponse
from sqlalchemy import func


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary_route():
    """
    获取仪表板汇总信息
    
    Returns:
        学习统计和状态信息
    """
    summary_data = get_dashboard_summary()
    
    # 获取总卡片数
    db = SessionLocal()
    try:
        total_cards = db.query(func.count(Card.id)).scalar() or 0
        total_questions = db.query(func.count(DbQuestionResponse.id)).scalar() or 0
    finally:
        db.close()
    
    # 计算整体记忆强度
    chapter_strengths = summary_data.get("chapter_strengths", {})
    if chapter_strengths:
        avg_strength = sum(chapter_strengths.values()) / len(chapter_strengths)
    else:
        avg_strength = 0.5
    
    # 格式化最近状态
    recent_states = []
    if summary_data.get("recent_state"):
        recent_states = [{"state": summary_data["recent_state"]}]
    
    return DashboardSummary(
        due_cards_today=summary_data.get("today_due_cards", 0),
        streak_days=summary_data.get("streak_days", 0),
        overall_memory_strength=avg_strength,
        chapter_strengths=chapter_strengths,
        recent_states=recent_states,
        total_cards=total_cards,
        total_questions_answered=total_questions
    )
