import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any

# 添加项目根路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from p1_algorithms.memory_engine import review_card, get_memory_strength, get_forgetting_curve
from p1_algorithms.schemas import CardData
from p2_knowledge.db_service import get_next_card as db_get_next_card
from p2_knowledge.db_service import update_card_memory as db_update_card_memory
from p2_knowledge.db_service import get_all_curves
from p2_knowledge.db_service import get_review_queue as db_get_review_queue


def get_next_card(chapter: Optional[int] = None, mode: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    获取下一张卡片。mode: 'learn'=新卡, 'review'=已学且到期, None=原行为
    """
    card_data = db_get_next_card(chapter, mode)
    if not card_data:
        return None
    
    # 计算当前记忆强度
    card_obj = CardData(
        id=card_data["id"],
        concept=card_data["concept"],
        front=card_data["front"],
        back=card_data["back"],
        chapter=card_data["chapter"],
        difficulty=card_data["difficulty"],
        memory_strength=card_data["memory_strength"],
        stability=card_data["stability"],
        easiness_factor=card_data["easiness_factor"],
        repetitions=card_data["repetitions"],
        next_review_at=card_data["next_review_at"],
        last_reviewed_at=card_data["last_reviewed_at"],
        related_concepts=card_data.get("related_concepts")
    )
    
    current_strength = get_memory_strength(card_obj)
    card_data["memory_strength"] = current_strength
    
    return card_data


def review_card_service(card_id: int, quality: int, session_id: int) -> Optional[Dict[str, Any]]:
    """
    处理卡片复习，更新记忆参数
    
    Args:
        card_id: 卡片ID
        quality: 用户评分 0-5
        session_id: 会话ID
    
    Returns:
        包含新记忆参数的字典，或 None
    """
    from p2_knowledge.database import SessionLocal
    from p2_knowledge.models.card import Card

    db = SessionLocal()
    try:
        card = db.query(Card).filter(Card.id == card_id).first()
        if not card:
            return None

        # 构造 CardData 对象
        card_obj = CardData(
            id=card.id,
            concept=card.concept,
            front=card.front,
            back=card.back,
            chapter=card.chapter,
            difficulty=card.difficulty,
            memory_strength=card.memory_strength,
            stability=card.stability,
            easiness_factor=card.easiness_factor,
            repetitions=card.repetitions,
            next_review_at=card.next_review_at,
            last_reviewed_at=card.last_reviewed_at,
            related_concepts=card.related_concepts
        )
        
        # 使用记忆引擎计算新参数（返回 CardData 对象，用属性访问）
        result = review_card(card_obj, quality)

        # 更新数据库
        updates = {
            "next_review_at": result.next_review_at,
            "memory_strength": result.memory_strength,
            "stability": result.stability,
            "easiness_factor": result.easiness_factor,
            "repetitions": result.repetitions,
            "last_reviewed_at": result.last_reviewed_at,
        }

        db_update_card_memory(card_id, updates)

        # 计算间隔天数
        interval_days = (result.next_review_at - datetime.utcnow()).days

        return {
            "next_review_at": result.next_review_at,
            "new_memory_strength": result.memory_strength,
            "interval_days": max(1, interval_days),
        }
    finally:
        db.close()


def get_review_queue(limit: int = 50, chapter: Optional[int] = None) -> list:
    """返回待复习卡片列表，直接透传 db_service 结果。"""
    return db_get_review_queue(limit, chapter)


def get_curves() -> Dict[str, Any]:
    """
    获取所有章节的遗忘曲线
    
    Returns:
        包含各章节曲线数据的字典
    """
    all_cards = get_all_curves()
    
    chapter_curves = {}
    
    for card_dict in all_cards:
        chapter = card_dict["chapter"]
        if chapter not in chapter_curves:
            chapter_curves[chapter] = []
        
        card_obj = CardData(
            id=card_dict["id"],
            concept=card_dict["concept"],
            front=card_dict["front"],
            back=card_dict["back"],
            chapter=card_dict["chapter"],
            difficulty=card_dict["difficulty"],
            memory_strength=card_dict["memory_strength"],
            stability=card_dict["stability"],
            easiness_factor=card_dict["easiness_factor"],
            repetitions=card_dict["repetitions"],
            next_review_at=card_dict["next_review_at"],
            last_reviewed_at=card_dict["last_reviewed_at"],
            related_concepts=card_dict.get("related_concepts")
        )
        
        curve = get_forgetting_curve(card_obj, days=14)
        chapter_curves[chapter].append(curve)
    
    # 计算每个章节的平均曲线
    result_curves = []
    for chapter, curves in chapter_curves.items():
        if curves:
            avg_curve = []
            num_cards = len(curves)
            for day in range(15):
                total_strength = sum(c[day]["strength"] for c in curves)
                avg_strength = total_strength / num_cards
                avg_curve.append({"day": day, "strength": avg_strength})
            result_curves.append({"chapter": chapter, "points": avg_curve})
    
    return {"curves": result_curves}
