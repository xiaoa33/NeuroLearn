from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# 加载项目根目录的 .env 环境变量文件
# 优先读取环境变量，未配置时使用默认 SQLite 路径
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./p2_knowledge/neurolearn.db")

# 创建 SQLAlchemy 引擎
# SQLite 需特殊配置 check_same_thread=False（多线程访问要求）
# 其他数据库（如 PostgreSQL/MySQL）无需此参数
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    # 可选：开启 SQL 语句打印（开发调试用）
    echo=False
)

# 创建数据库会话工厂
# 配置：禁止自动提交、禁止自动刷新，绑定到上述引擎
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 定义 ORM 模型基类
# 所有模型（card/question/session/response）需继承此类
Base = declarative_base()

def get_db():
    """
    数据库会话依赖函数（供 P3 层 FastAPI 路由使用）
    提供自动创建/关闭会话的上下文，保证连接安全释放
    使用方式：在 FastAPI 路由中通过 Depends(get_db) 注入
    """
    db = SessionLocal()
    try:
        # 生成数据库会话对象
        yield db
    finally:
        # 无论是否异常，最终关闭会话
        db.close()
