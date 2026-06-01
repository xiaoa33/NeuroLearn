"""
数据库 CRUD 服务层
P3 层访问数据库的唯一入口，严格遵循 README 接口契约 6.2
实现所有数据读写、聚合查询、业务逻辑封装
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, cast, Date
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

# 导入 ORM 模型
from p2_knowledge.models.card import Card
from p2_knowledge.models.question import Question
from p2_knowledge.models.session import LearningSession
from p2_knowledge.models.response import QuestionResponse


# ==================== 知识卡片 CRUD ====================
def get_next_card(db: Session, chapter: Optional[int] = None) -> Optional[Card]:
    """
    获取下一张待复习的卡片
    规则：按下次复习时间升序，优先取已到期的卡片，支持按章节筛选
    :param db: 数据库会话
    :param chapter: 章节号（可选）
    :return: 待复习卡片 / None
    """
    query = db.query(Card).filter(Card.next_review_at <= datetime.utcnow())
    if chapter:
        query = query.filter(Card.chapter == chapter)
    # 按复习时间升序，取最早需要复习的
    return query.order_by(Card.next_review_at.asc()).first()


def update_card_memory(db: Session, card_id: int, updates: Dict[str, Any]) -> Optional[Card]:
    """
    更新卡片的 SM-2 记忆参数（由 P1 算法计算）
    :param db: 数据库会话
    :param card_id: 卡片ID
    :param updates: 参数字典（memory_strength/stability/easiness_factor等）
    :return: 更新后的卡片
    """
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        return None
    # 批量更新字段
    for key, value in updates.items():
        setattr(card, key, value)
    # 自动更新最后复习时间
    card.last_reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(card)
    return card


def get_all_curves(db: Session) -> List[Dict[str, Any]]:
    """
    获取所有卡片的稳定性参数，用于生成遗忘曲线
    :return: 包含卡片ID、稳定性、下次复习时间的列表
    """
    cards = db.query(Card.id, Card.stability, Card.next_review_at).all()
    return [
        {"card_id": c.id, "stability": c.stability, "next_review_at": c.next_review_at}
        for c in cards
    ]


def bulk_insert_cards(db: Session, chapter: int, cards: List[Dict[str, Any]]) -> int:
    """
    批量插入章节卡片（供生成脚本使用）
    :param db: 数据库会话
    :param chapter: 章节号
    :param cards: 卡片字典列表
    :return: 插入成功的数量
    """
    card_objects = []
    for card_data in cards:
        card = Card(
            chapter=chapter,
            concept=card_data["concept"],
            front=card_data["front"],
            back=card_data["back"],
            difficulty=card_data["difficulty"],
            related_concepts=card_data.get("related_concepts", []),
            # 初始化记忆参数
            memory_strength=0.0,
            stability=0.0,
            easiness_factor=2.5,
            repetitions=0,
            next_review_at=datetime.utcnow()
        )
        card_objects.append(card)
    db.bulk_save_objects(card_objects)
    db.commit()
    return len(card_objects)


# ==================== 题目 CRUD ====================
def get_next_question(
        db: Session,
        chapter: int,
        difficulty: int,
        exclude_recent: int = 5
) -> Optional[Question]:
    """
    随机获取下一道题目
    规则：指定章节+难度，排除最近5题，随机返回1道
    :param db: 数据库会话
    :param chapter: 章节号
    :param difficulty: 难度(1/2/3)
    :param exclude_recent: 排除最近N题
    :return: 题目 / None
    """
    # 1. 获取最近答过的题目ID
    recent_responses = db.query(QuestionResponse.question_id).order_by(QuestionResponse.id.desc()).limit(
        exclude_recent).all()
    recent_ids = [r.question_id for r in recent_responses]

    # 2. 查询符合条件的题目（排除最近）
    query = db.query(Question).filter(
        and_(
            Question.chapter == chapter,
            Question.difficulty == difficulty
        )
    )
    if recent_ids:
        query = query.filter(Question.id.not_in(recent_ids))

    # 3. 随机返回1题
    return query.order_by(func.random()).first()


# ==================== 答题记录 CRUD ====================
def save_response(
        db: Session,
        session_id: int,
        question_id: int,
        is_correct: bool,
        time_ms: int,
        difficulty: int
) -> QuestionResponse:
    """
    保存单题答题结果
    :param db: 数据库会话
    :param session_id: 学习会话ID
    :param question_id: 题目ID
    :param is_correct: 是否答对
    :param time_ms: 答题耗时(毫秒)
    :param difficulty: 题目难度
    :return: 答题记录
    """
    response = QuestionResponse(
        session_id=session_id,
        question_id=question_id,
        is_correct=is_correct,
        time_ms=time_ms,
        difficulty=difficulty,
        answered_at=datetime.utcnow()
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    return response


# ==================== 学习会话 CRUD ====================
def create_session(db: Session, user_id: int = 1) -> LearningSession:
    """
    创建新的学习会话
    :param db: 数据库会话
    :param user_id: 用户ID
    :return: 新建的会话
    """
    session = LearningSession(
        user_id=user_id,
        start_time=datetime.utcnow(),
        status="in_progress"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def end_session(
        db: Session,
        session_id: int,
        sam_score: float,
        total_cards: int,
        total_questions: int,
        accuracy: float
) -> Optional[LearningSession]:
    """
    结束学习会话，更新统计数据
    :param db: 数据库会话
    :param session_id: 会话ID
    :param sam_score: SAM得分
    :param total_cards: 复习卡片数
    :param total_questions: 答题数
    :param accuracy: 正确率
    :return: 结束后的会话
    """
    session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
    if not session:
        return None
    session.status = "finished"
    session.end_time = datetime.utcnow()
    session.sam_score = sam_score
    session.total_cards_reviewed = total_cards
    session.total_questions_answered = total_questions
    session.accuracy = accuracy
    db.commit()
    db.refresh(session)
    return session


# ==================== 仪表盘/统计查询 ====================
def get_dashboard_summary(db: Session, user_id: int = 1) -> Dict[str, Any]:
    """
    获取仪表盘汇总数据
    :return: 到期卡片数、连续学习天数、章节平均记忆强度、总卡片数等
    """
    now = datetime.utcnow()
    today = now.date()

    # 1. 到期待复习卡片数
    due_cards = db.query(Card).filter(Card.next_review_at <= now).count()

    # 2. 总卡片数
    total_cards = db.query(Card).count()

    # 3. 平均记忆稳定性
    avg_stability = db.query(func.avg(Card.stability)).scalar() or 0.0

    # 4. 今日完成会话数
    today_sessions = db.query(LearningSession).filter(
        and_(
            LearningSession.user_id == user_id,
            cast(LearningSession.start_time, Date) == today,
            LearningSession.status == "finished"
        )
    ).count()

    # 5. 连续学习天数（简化版：最近7天有学习则连续）
    consecutive_days = 0
    for i in range(7):
        day = today - timedelta(days=i)
        has_session = db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                cast(LearningSession.start_time, Date) == day,
                LearningSession.status == "finished"
            )
        ).first()
        if has_session:
            consecutive_days += 1
        else:
            break

    return {
        "due_cards_count": due_cards,
        "total_cards": total_cards,
        "avg_memory_stability": round(avg_stability, 2),
        "consecutive_study_days": consecutive_days,
        "today_sessions": today_sessions
    }


def get_state_history(db: Session, n_days: int = 7) -> List[Dict[str, Any]]:
    """
    获取最近 N 天的学习状态历史
    :param db: 数据库会话
    :param n_days: 天数
    :return: 每日学习数据列表
    """
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=n_days)

    # 按日期聚合统计
    daily_stats = db.query(
        cast(LearningSession.start_time, Date).label("date"),
        func.count(LearningSession.id).label("sessions_count"),
        func.sum(LearningSession.total_cards_reviewed).label("cards_reviewed"),
        func.sum(LearningSession.total_questions_answered).label("questions_answered"),
        func.avg(LearningSession.accuracy).label("avg_accuracy")
    ).filter(
        and_(
            LearningSession.status == "finished",
            cast(LearningSession.start_time, Date) >= start_date
        )
    ).group_by("date").order_by("date").all()

    result = []
    for stat in daily_stats:
        result.append({
            "date": stat.date.isoformat(),
            "sessions_count": stat.sessions_count,
            "cards_reviewed": stat.cards_reviewed or 0,
            "questions_answered": stat.questions_answered or 0,
            "avg_accuracy": round(stat.avg_accuracy, 2) if stat.avg_accuracy else 0.0
        })
    return result