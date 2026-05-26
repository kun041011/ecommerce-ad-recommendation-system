"""数据库连接配置

创建SQLAlchemy引擎和会话工厂，提供数据库会话的依赖注入生成器。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# 创建数据库引擎，check_same_thread=False 允许SQLite在多线程环境中使用
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# 创建会话工厂，关闭自动提交和自动刷新以便手动控制事务
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """所有ORM模型的基类"""
    pass


def get_db():
    """数据库会话依赖注入生成器，用于FastAPI的Depends

    使用方式: db: Session = Depends(get_db)
    会话在请求结束后自动关闭。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
