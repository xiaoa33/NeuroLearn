import sys
import os
from typing import Optional, Dict, Any, List

# 添加项目根路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from p1_algorithms.difficulty_scheduler import next_difficulty
from p1_algorithms.schemas import StateEnum
from p2_knowledge.db_service import get_next_question as db_get_next_question
from p2_knowledge.db_service import save_response

# 存储会话的答题历史
session_answers: Dict[int, List[bool]] = {}
# 存储会话的当前难度
session_difficulty: Dict[int, int] = {}


def get_next_question(chapter: int, difficulty: int, session_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    获取下一道题目
    
    Args:
        chapter: 章节
        difficulty: 难度 1-3
        session_id: 会话ID，可选
    
    Returns:
        题目数据字典，或 None
    """
    question_data = db_get_next_question(chapter, difficulty)
    if not question_data:
        return None
    
    # 存储当前难度
    if session_id:
        session_difficulty[session_id] = difficulty
    
    return question_data


def answer_question(question_id: int, answer: str, time_ms: int, session_id: int, state: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    处理用户答题，判断对错，更新难度
    
    Args:
        question_id: 题目ID
        answer: 用户答案
        time_ms: 答题耗时（毫秒）
        session_id: 会话ID
        state: 当前学习状态，可选
    
    Returns:
        包含答题结果的字典，或 None
    """
    from p2_knowledge.database import SessionLocal
    from p2_knowledge.models.question import Question
    
    db = SessionLocal()
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return None
        
        # 判断答案是否正确
        is_correct = _check_answer(answer, question.answer, question.type)
        
        # 更新会话答题历史
        if session_id not in session_answers:
            session_answers[session_id] = []
        session_answers[session_id].append(is_correct)
        # 只保留最近10条
        session_answers[session_id] = session_answers[session_id][-10:]
        
        # 获取当前难度
        current_difficulty = session_difficulty.get(session_id, 2)
        
        # 计算下一题难度
        recent = session_answers[session_id][-3:]
        sched = {
            "current_level": current_difficulty,
            "window": session_answers[session_id][:-3]
        }
        
        # 将前端传来的字符串映射到 StateEnum，无效值兜底为 flow
        try:
            state_enum = StateEnum(state) if state else StateEnum.flow
        except ValueError:
            state_enum = StateEnum.flow

        next_diff, reason = next_difficulty(sched, state_enum, recent)
        
        # 保存答题记录
        save_response(session_id, question_id, is_correct, time_ms, current_difficulty)
        
        return {
            "is_correct": is_correct,
            "correct_answer": question.answer,
            "explanation": question.explanation,
            "next_difficulty": next_diff,
            "reason": reason
        }
    finally:
        db.close()


def _check_answer(user_answer: str, correct_answer: str, question_type: str) -> bool:
    """
    检查答案是否正确
    
    Args:
        user_answer: 用户答案
        correct_answer: 正确答案
        question_type: 题目类型
    
    Returns:
        是否正确
    """
    user_answer = user_answer.strip().lower()
    correct_answer = correct_answer.strip().lower()
    
    if question_type == "truefalse":
        user_answer = user_answer.replace("true", "1").replace("false", "0").replace("t", "1").replace("f", "0")
        correct_answer = correct_answer.replace("true", "1").replace("false", "0").replace("t", "1").replace("f", "0")
    
    return user_answer == correct_answer
