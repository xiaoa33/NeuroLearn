from sqlalchemy import Column, Integer, Float, DateTime, String, JSON
from datetime import datetime
from p2_knowledge.database import Base


class LearningSession(Base):
    """
    学习会话表 (learning_sessions)
    记录一次学习的完整生命周期、得分、统计数据及状态日志
    """
    __tablename__ = "learning_sessions"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 会话时间：修正字段名为 started_at/ended_at
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="会话开始时间")
    ended_at = Column(DateTime, nullable=True, comment="会话结束时间")

    # 会话状态与评分
    # 修正：SAM 拆分为 valence 和 arousal
    sam_valence = Column(Float, default=0.0, comment="SAM效价轴得分")
    sam_arousal = Column(Float, default=0.0, comment="SAM唤醒轴得分")

    # 会话状态日志 (JSON数组)
    state_log = Column(JSON, default=list, comment="会话状态变化日志")

    # 对应文档 4.3 的 final_state
    final_state = Column(String, nullable=True, comment="会话末尾状态枚举")

    # 学习统计：修正字段名
    cards_reviewed = Column(Integer, default=0, comment="本次复习卡片总数")
    questions_answered = Column(Integer, default=0, comment="本次答题总数")

    # 可选：用户标识
    user_id = Column(Integer, default=1, index=True, comment="用户ID")