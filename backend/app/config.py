from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/ecommerce.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ACTIVITY_DECAY_LAMBDA: float = 0.1
    ACTIVITY_UPDATE_INTERVAL_SECONDS: int = 3600

    model_config = {"env_file": ".env"}


settings = Settings()
