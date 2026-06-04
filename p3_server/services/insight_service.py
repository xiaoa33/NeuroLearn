import sys
import os
from typing import Dict, Any
import random

# 添加项目根路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_insight_suggestion() -> Dict[str, str]:
    """
    获取学习洞察建议（模拟数据）
    
    Returns:
        包含即时建议和今日计划建议的字典
    """
    from p2_knowledge.db_service import get_dashboard_summary as db_get_dashboard_summary
    
    try:
        dashboard_data = db_get_dashboard_summary()
        due_cards = dashboard_data.get("today_due_cards", 0)
        recent_state = dashboard_data.get("recent_state")
    except:
        due_cards = 0
        recent_state = None
    
    # 生成即时建议
    instant_advice = _generate_instant_advice(due_cards, recent_state)
    
    # 生成今日计划建议
    today_plan = _generate_today_plan(due_cards)
    
    return {
        "instant_advice": instant_advice,
        "today_plan": today_plan
    }


def _generate_instant_advice(due_cards: int, recent_state: str) -> str:
    """
    生成即时建议
    
    Args:
        due_cards: 今日到期卡片数
        recent_state: 最近学习状态
    
    Returns:
        建议文本
    """
    advices = []
    
    if due_cards > 10:
        advices.append(f"你有 {due_cards} 张卡片需要复习，建议优先完成复习任务！")
    elif due_cards > 0:
        advices.append(f"今天有 {due_cards} 张卡片等待复习，保持记忆节奏很重要。")
    else:
        advices.append("今天没有需要复习的卡片，很棒！可以学习一些新内容。")
    
    state_advice = {
        "flow": ["你最近状态很好，继续保持这个节奏！"],
        "anxiety": ["记得适当放松，学习不是一蹴而就的。"],
        "boredom": ["试试学习一些新章节，增加学习的新鲜感。"],
        "confusion": ["建议先复习一些基础知识，再继续新内容。"],
        "fatigue": ["注意劳逸结合，适当的休息能提高学习效率。"]
    }
    
    if recent_state in state_advice:
        advices.extend(state_advice[recent_state])
    
    # 添加一些通用建议
    general_advices = [
        "每次学习 25 分钟休息 5 分钟，保持专注度。",
        "定期回顾卡片，巩固记忆效果更好。",
        "尝试用自己的话复述知识点，加深理解。"
    ]
    
    advices.extend(general_advices)
    
    return random.choice(advices)


def _generate_today_plan(due_cards: int) -> str:
    """
    生成今日计划建议
    
    Args:
        due_cards: 今日到期卡片数
    
    Returns:
        计划建议文本
    """
    plans = [
        "建议先完成卡片复习，再做 10-15 道练习题巩固知识。",
        "今天可以安排 30 分钟复习，45 分钟学习新内容。",
        "尝试完成一个小的学习目标，比如掌握一个章节的核心概念。",
        "利用碎片时间复习卡片，整块时间学习新内容效果更好。"
    ]
    
    if due_cards > 15:
        plans.insert(0, "今天复习任务较重，建议优先集中精力完成卡片复习。")
    
    return random.choice(plans)
