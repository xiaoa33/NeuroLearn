import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# 添加项目根路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from p1_algorithms.state_scorer import score_state
from p1_algorithms.schemas import BehaviorSignal as P1BehaviorSignal
from p1_algorithms.schemas import SAMScore as P1SAMScore
from p1_algorithms.schemas import CameraScore as P1CameraScore
from p1_algorithms.schemas import StateEnum
from p2_knowledge.db_service import get_state_history as db_get_state_history

# 存储会话的状态记录
session_states: Dict[int, Dict[str, Any]] = {}


def report_state(
    behavior: Dict[str, Any],
    sam: Dict[str, Any],
    camera: Optional[Dict[str, Any]] = None,
    session_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    报告学习状态并计算评分
    
    Args:
        behavior: 行为信号字典
        sam: SAM量表字典
        camera: 摄像头信号字典，可选
        session_id: 会话ID，可选
    
    Returns:
        包含状态、评分和建议的字典
    """
    # 构造 P1 算法的数据类（字段名以 p1_algorithms/schemas.py 为准）
    behavior_signal = P1BehaviorSignal(
        accuracy=behavior["correct_rate"],
        avg_time_zscore=behavior.get("avg_time_zscore") or 0.0,
        unfocus_count=behavior.get("unfocus_count", 0),
        pause_duration=0.0,
    )

    sam_score = P1SAMScore(
        valence=sam["valence"],
        arousal=sam["arousal"],
    )

    camera_score = None
    if camera:
        camera_score = P1CameraScore(
            focus_score=camera.get("attention", 0.5),
            blink_rate=camera.get("blink_rate", 15.0),
            head_offset=camera.get("head_offset", 0.0),
        )
    
    # 计算会话时长（分钟），用于疲劳判断
    session_duration_minutes = 0.0
    if session_id:
        from p2_knowledge.database import SessionLocal
        from p2_knowledge.models.session import LearningSession
        _db = SessionLocal()
        try:
            _session = _db.query(LearningSession).filter(LearningSession.id == session_id).first()
            if _session and _session.started_at:
                session_duration_minutes = (datetime.utcnow() - _session.started_at).total_seconds() / 60
        finally:
            _db.close()

    # 调用状态评分算法
    state, total_score, weights = score_state(behavior_signal, sam_score, camera_score, session_duration_minutes)
    
    # 生成建议文本
    suggestion_text = _generate_suggestion(state, total_score)
    
    # 保存会话状态
    if session_id:
        session_states[session_id] = {
            "state": state,
            "score": total_score,
            "sam_valence": sam["valence"],
            "sam_arousal": sam["arousal"]
        }
    
    return {
        "state": state,
        "score": total_score,
        "weights": weights,
        "suggestion_text": suggestion_text
    }


def get_state_history(n_days: int = 7) -> List[Dict[str, Any]]:
    """
    获取最近 n 天的状态历史
    
    Args:
        n_days: 天数
    
    Returns:
        状态记录列表
    """
    from p2_knowledge.database import SessionLocal
    from p2_knowledge.models.session import LearningSession
    from datetime import timedelta, datetime
    
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=n_days)
        sessions = db.query(LearningSession)\
            .filter(LearningSession.ended_at >= cutoff)\
            .filter(LearningSession.final_state.isnot(None))\
            .order_by(LearningSession.ended_at)\
            .all()
        
        result = []
        for session in sessions:
            result.append({
                "date": session.ended_at.date().isoformat() if session.ended_at else "",
                "session_id": session.id,
                "state": session.final_state,
                "sam_valence": session.sam_valence,
                "sam_arousal": session.sam_arousal,
                "cards_reviewed": session.cards_reviewed or 0,
                "questions_answered": session.questions_answered or 0
            })
        
        return result
    finally:
        db.close()


def _generate_suggestion(state: StateEnum, score: float) -> str:
    """
    根据状态和评分生成建议文本
    
    Args:
        state: 学习状态
        score: 综合评分
    
    Returns:
        建议文本
    """
    suggestions = {
        StateEnum.flow: [
            "太棒了！你正处于心流状态，保持这个状态继续学习吧！",
            "状态很好，继续保持当前的学习节奏。",
            "你现在学习效率很高，利用这个优势多学一些内容。"
        ],
        StateEnum.anxiety: [
            "别担心，学习需要慢慢来。先休息一下，做几次深呼吸。",
            "建议降低一点难度，从简单的内容开始重建信心。",
            "焦虑是正常的，试着把大任务分解成小目标来完成。"
        ],
        StateEnum.boredom: [
            "看起来有点无聊了，试试挑战一些更难的内容！",
            "换一种学习方式，或者学习新的章节来增加新鲜感。",
            "可以尝试设置一些小挑战，让学习更有趣味性。"
        ],
        StateEnum.confusion: [
            "遇到困惑很正常，试着重新阅读相关概念或例题。",
            "建议先巩固一下基础知识，再继续当前内容。",
            "可以尝试画个思维导图来理清思路。"
        ],
        StateEnum.fatigue: [
            "你看起来累了，先休息一下吧！喝杯水，活动活动身体。",
            "疲劳时学习效率会下降，建议暂停学习，充分休息。",
            "试着做一些简单的伸展运动，或者小睡一会儿。"
        ]
    }
    
    import random
    return random.choice(suggestions.get(state, suggestions[StateEnum.flow]))
