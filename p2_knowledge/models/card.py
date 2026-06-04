from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from datetime import datetime
from p2_knowledge.database import Base


class Card(Base):
    """
    知识卡片表 (cards)
    存储学习卡片内容 + SM-2 记忆追踪参数
    """
    __tablename__ = "cards"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 卡片基础信息
    chapter = Column(Integer, index=True, nullable=False, comment="所属章节")
    concept = Column(String(255), index=True, nullable=False, comment="核心概念名称")
    front = Column(String, nullable=False, comment="卡片正面（问题）")
    back = Column(String, nullable=False, comment="卡片背面（答案）")

    # 难度：1基础/2理解/3应用
    difficulty = Column(Integer, nullable=False, comment="卡片难度：1=简单/2=中等/3=困难")

    # SM-2 记忆算法核心参数
    memory_strength = Column(Float, default=1.0, comment="记忆强度")
    stability = Column(Float, default=1.0, comment="记忆稳定性（遗忘曲线核心参数）")
    easiness_factor = Column(Float, default=2.5, comment="易度因子（初始值2.5）")
    repetitions = Column(Integer, default=0, comment="累计复习次数")

    # 复习时间管理
    next_review_at = Column(DateTime, default=datetime.utcnow, comment="下次复习时间")
    last_reviewed_at = Column(DateTime, nullable=True, comment="上次复习时间")

    # 扩展字段
    related_concepts = Column(JSON, default=list, comment="关联概念列表（JSON格式）")

    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")