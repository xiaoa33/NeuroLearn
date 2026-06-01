from sqlalchemy import Column, Integer, Boolean, Float, DateTime, ForeignKey
from datetime import datetime
from p2_knowledge.database import Base


class QuestionResponse(Base):
    """
    答题明细表 (question_responses)
    记录每一次答题的对错、耗时、难度等明细数据
    """
    __tablename__ = "question_responses"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 外键：关联学习会话 + 题目
    session_id = Column(Integer, ForeignKey("learning_sessions.id", ondelete="CASCADE"), index=True, nullable=False,
                        comment="所属会话ID")
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False,
                         comment="题目ID")

    # 答题结果
    is_correct = Column(Boolean, nullable=False, comment="是否答对")

    # 答题耗时（毫秒）
    time_spent_ms = Column(Integer, nullable=False, comment="答题耗时（毫秒）")

    # 答题时题目难度：修正字段名以匹配文档 difficulty_at_time
    difficulty_at_time = Column(Integer, nullable=False, comment="答题时的当前难度级别")

    # 答题时间
    answered_at = Column(DateTime, default=datetime.utcnow, comment="答题时间")