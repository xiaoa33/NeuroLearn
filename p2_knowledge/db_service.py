"""
数据库 CRUD 服务层
P3 层访问数据库的唯一入口，严格遵循 README 接口契约 6.2
所有函数自行管理 db session，调用方无需传入 Session 对象。
"""
import math
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from p2_knowledge.database import SessionLocal  # re-export 供 p3 services 直接 import
from p2_knowledge.models.card import Card
from p2_knowledge.models.question import Question
from p2_knowledge.models.session import LearningSession
from p2_knowledge.models.response import QuestionResponse


def _card_to_dict(card: Card) -> Dict[str, Any]:
    return {
        "id": card.id,
        "chapter": card.chapter,
        "concept": card.concept,
        "front": card.front,
        "back": card.back,
        "difficulty": card.difficulty,
        "memory_strength": card.memory_strength,
        "stability": card.stability,
        "easiness_factor": card.easiness_factor,
        "repetitions": card.repetitions,
        "next_review_at": card.next_review_at,
        "last_reviewed_at": card.last_reviewed_at,
        "related_concepts": card.related_concepts,
    }


# ==================== 知识卡片 CRUD ====================

def get_next_card(chapter: Optional[int] = None, mode: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    获取下一张卡片。mode 参数控制返回类型：
    - 'learn'：仅返回从未学习的卡片（repetitions == 0）
    - 'review'：仅返回已学习且已到期的卡片（repetitions > 0, next_review_at <= now）
    - None：原行为（到期卡 or 新卡），兜底返回最早的卡片
    """
    db = SessionLocal()
    try:
        base = db.query(Card)
        if chapter:
            base = base.filter(Card.chapter == chapter)

        now = datetime.utcnow()

        if mode == 'learn':
            card = base.filter(Card.repetitions == 0).order_by(Card.next_review_at.asc()).first()
        elif mode == 'review':
            card = (
                base.filter(Card.repetitions > 0, Card.next_review_at <= now)
                .order_by(Card.next_review_at.asc())
                .first()
            )
        else:
            card = (
                base.filter((Card.next_review_at <= now) | (Card.repetitions == 0))
                .order_by(Card.next_review_at.asc())
                .first()
            )
            if card is None:
                card = base.order_by(Card.next_review_at.asc()).first()

        return _card_to_dict(card) if card else None
    finally:
        db.close()


def update_card_memory(card_id: int, updates: Dict[str, Any]) -> bool:
    """将 P1 算法计算结果（新稳定性、下次复习时间等）写入 cards 表。"""
    db = SessionLocal()
    try:
        card = db.query(Card).filter(Card.id == card_id).first()
        if not card:
            return False
        for key, value in updates.items():
            setattr(card, key, value)
        db.commit()
        return True
    finally:
        db.close()


def get_review_queue(limit: int = 50, chapter: Optional[int] = None) -> List[Dict[str, Any]]:
    """返回已学习且到期的待复习卡片（repetitions > 0），按紧迫程度排序。"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        query = db.query(Card).filter(Card.repetitions > 0, Card.next_review_at <= now)
        if chapter:
            query = query.filter(Card.chapter == chapter)
        cards = query.order_by(Card.next_review_at.asc()).limit(limit).all()
        return [_card_to_dict(c) for c in cards]
    finally:
        db.close()


def get_all_curves() -> List[Dict[str, Any]]:
    """返回所有卡片的完整参数，供 P3 调用 P1 get_forgetting_curve() 后组装遗忘曲线。"""
    db = SessionLocal()
    try:
        cards = db.query(Card).all()
        return [_card_to_dict(c) for c in cards]
    finally:
        db.close()


def bulk_insert_cards(chapter: int, cards: List[Dict[str, Any]]) -> int:
    """批量插入章节卡片（供生成脚本使用）。"""
    db = SessionLocal()
    try:
        card_objects = [
            Card(
                chapter=chapter,
                concept=c["concept"],
                front=c["front"],
                back=c["back"],
                difficulty=c["difficulty"],
                related_concepts=c.get("related_concepts", []),
                memory_strength=1.0,
                stability=1.0,
                easiness_factor=2.5,
                repetitions=0,
                next_review_at=datetime.utcnow(),
            )
            for c in cards
        ]
        db.bulk_save_objects(card_objects)
        db.commit()
        return len(card_objects)
    finally:
        db.close()


# ==================== 题目 CRUD ====================

def get_next_question(
    chapter: int,
    difficulty: int,
    exclude_recent: int = 5,
) -> Optional[Dict[str, Any]]:
    """
    随机获取下一道题目。
    指定章节+难度，排除最近 5 题，随机返回 1 道。
    """
    db = SessionLocal()
    try:
        recent_ids = [
            r.question_id
            for r in db.query(QuestionResponse.question_id)
            .order_by(QuestionResponse.id.desc())
            .limit(exclude_recent)
            .all()
        ]
        query = db.query(Question).filter(
            and_(Question.chapter == chapter, Question.difficulty == difficulty)
        )
        if recent_ids:
            query = query.filter(Question.id.not_in(recent_ids))
        q = query.order_by(func.random()).first()
        if not q:
            return None
        return {
            "id": q.id,
            "chapter": q.chapter,
            "stem": q.stem,
            "options": q.options,
            "answer": q.answer,
            "explanation": q.explanation,
            "type": q.type,
            "difficulty": q.difficulty,
            "related_card_id": q.related_card_id,
        }
    finally:
        db.close()


# ==================== 答题记录 CRUD ====================

def save_response(
    session_id: int,
    question_id: int,
    is_correct: bool,
    time_ms: int,
    difficulty: int,
) -> bool:
    """在 question_responses 表写入一条答题记录。"""
    db = SessionLocal()
    try:
        response = QuestionResponse(
            session_id=session_id,
            question_id=question_id,
            is_correct=is_correct,
            time_spent_ms=time_ms,
            difficulty_at_time=difficulty,
            answered_at=datetime.utcnow(),
        )
        db.add(response)
        db.commit()
        return True
    finally:
        db.close()


# ==================== 学习会话 CRUD ====================

def create_session() -> int:
    """在 learning_sessions 表插入新行，返回自增主键 session_id。"""
    db = SessionLocal()
    try:
        session = LearningSession(started_at=datetime.utcnow())
        db.add(session)
        db.commit()
        db.refresh(session)
        return session.id
    finally:
        db.close()


def end_session(
    session_id: int,
    final_state: Optional[str] = None,
    sam_valence: Optional[float] = None,
    sam_arousal: Optional[float] = None,
    cards_reviewed: int = 0,
    questions_answered: int = 0,
) -> bool:
    """更新会话的 ended_at、final_state 和 SAM 得分。"""
    db = SessionLocal()
    try:
        session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if not session:
            return False
        session.ended_at = datetime.utcnow()
        session.final_state = final_state
        if sam_valence is not None:
            session.sam_valence = sam_valence
        if sam_arousal is not None:
            session.sam_arousal = sam_arousal
        session.cards_reviewed = cards_reviewed or 0
        session.questions_answered = questions_answered or 0
        db.commit()
        return True
    finally:
        db.close()


# ==================== 仪表盘/统计查询 ====================

def get_dashboard_summary() -> Dict[str, Any]:
    """聚合查询：今日到期卡片数、连续天数、各章节 memory_strength 均值。"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        today = now.date()

        # 今日待复习：仅计已学习（repetitions > 0）且到期的卡片
        due_cards = db.query(Card).filter(Card.next_review_at <= now, Card.repetitions > 0).count()
        total_cards = db.query(Card).count()

        # 各章节实时记忆强度：仅统计已学习的卡片（repetitions > 0），实时计算 R(t)=e^(-t/S)
        chapter_sums: Dict[int, list] = {}
        learned_cards = db.query(Card).filter(Card.repetitions > 0).all()
        for card in learned_cards:
            if card.last_reviewed_at:
                t = max(0.0, (now - card.last_reviewed_at).total_seconds() / 86400)
                strength = math.exp(-t / max(card.stability, 0.01))
            else:
                strength = card.memory_strength
            chapter_sums.setdefault(card.chapter, []).append(strength)
        chapter_strengths: Dict[int, float] = {
            ch: round(sum(vals) / len(vals), 4)
            for ch, vals in chapter_sums.items()
        }

        # 连续学习天数：只要当天有打开网站（session 被创建）即算
        # 用时间区间查询替代 cast(Date)，避免 SQLite 不支持 Date 类型转换的问题
        # 若今天还未开启会话，从昨天开始计算（今天尚未结束，不应打断连续记录）
        def has_session_on(day):
            day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
            day_end = day_start + timedelta(days=1)
            return db.query(LearningSession).filter(
                LearningSession.started_at >= day_start,
                LearningSession.started_at < day_end,
            ).first() is not None

        consecutive_days = 0
        start_offset = 0 if has_session_on(today) else 1
        for i in range(start_offset, 30 + start_offset):
            day = today - timedelta(days=i)
            if has_session_on(day):
                consecutive_days += 1
            else:
                break

        total_cards_reviewed = db.query(Card).filter(Card.repetitions > 0).count()

        return {
            "due_cards_today": due_cards,
            "streak_days": consecutive_days,
            "chapter_strengths": chapter_strengths,
            "total_cards": total_cards,
            "total_cards_reviewed": total_cards_reviewed,
            "total_questions_answered": db.query(QuestionResponse).count(),
            "recent_states": [],
        }
    finally:
        db.close()


def get_state_history(n_days: int = 7) -> List[Dict[str, Any]]:
    """返回最近 n 天每次会话末尾的状态记录。"""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=n_days)
        sessions = (
            db.query(LearningSession)
            .filter(LearningSession.ended_at.isnot(None))
            .filter(LearningSession.ended_at >= cutoff)
            .order_by(LearningSession.ended_at)
            .all()
        )
        return [
            {
                "date": s.ended_at.date().isoformat() if s.ended_at else "",
                "session_id": s.id,
                "state": s.final_state or "flow",
                "sam_valence": s.sam_valence,
                "sam_arousal": s.sam_arousal,
                "cards_reviewed": s.cards_reviewed or 0,
                "questions_answered": s.questions_answered or 0,
            }
            for s in sessions
        ]
    finally:
        db.close()
