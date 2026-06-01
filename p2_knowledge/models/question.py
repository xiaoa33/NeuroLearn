from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from p2_knowledge.database import Base


class Question(Base):
    """
    练习题表 (questions)
    存储题库内容：题干、选项、答案、解析、题型、难度
    """
    __tablename__ = "questions"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 外键：关联知识卡片
    related_card_id = Column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), index=True, nullable=True,
                             comment="关联卡片ID（可为空）")

    # 题目基础信息
    chapter = Column(Integer, index=True, nullable=False, comment="所属章节")
    stem = Column(String, nullable=False, comment="题干")

    # 选项列表（JSON格式），文档未强制非空（填空题可能不需要选项）
    options = Column(JSON, nullable=True, comment="选项列表（JSON格式）")

    answer = Column(String, nullable=False, comment="正确答案")
    explanation = Column(String, nullable=True, comment="答案解析")

    # 题型：choice/truefalse/fill，默认为 choice
    type = Column(String, default="choice", comment="题型：choice/truefalse/fill")

    # 题目难度：1/2/3
    difficulty = Column(Integer, index=True, nullable=False, comment="题目难度：1/2/3")