"""
数据库初始化脚本
执行命令：python -m p2_knowledge.scripts.seed_db
"""
from p2_knowledge.database import engine, Base
# 导入所有模型，让SQLAlchemy识别表结构
from p2_knowledge.models.card import Card
from p2_knowledge.models.question import Question
from p2_knowledge.models.session import LearningSession
from p2_knowledge.models.response import QuestionResponse

def init_database():
    """创建所有数据库表（不存在则创建）"""
    print("正在初始化数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    print(f"已创建表：{[table.name for table in Base.metadata.sorted_tables]}")

if __name__ == "__main__":
    init_database()
