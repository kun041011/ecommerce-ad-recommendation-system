"""系统配置

使用pydantic-settings管理应用配置，支持从环境变量和.env文件加载。
包含数据库连接、Redis缓存、JWT认证和活跃度衰减等核心配置项。
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用全局配置类，支持环境变量覆盖"""
    DATABASE_URL: str = "sqlite:///./data/ecommerce.db"            # 数据库连接URL，默认使用SQLite
    REDIS_URL: str = "redis://localhost:6379/0"                    # Redis连接URL，用于缓存和频控计数
    SECRET_KEY: str = "dev-secret-key-change-in-production"        # JWT签名密钥，生产环境必须修改
    ALGORITHM: str = "HS256"                                       # JWT签名算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60                          # JWT令牌过期时间（分钟）
    ACTIVITY_DECAY_LAMBDA: float = 0.1                             # 活跃度指数衰减系数λ，值越大衰减越快
    ACTIVITY_UPDATE_INTERVAL_SECONDS: int = 3600                   # 活跃度评分更新间隔（秒）

    model_config = {"env_file": ".env"}  # 从.env文件读取配置


settings = Settings()  # 全局配置单例
