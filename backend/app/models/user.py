import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    consumer = "consumer"
    merchant = "merchant"
    admin = "admin"


class AdFrequencyLevel(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.consumer)
    activity_score: Mapped[float] = mapped_column(Float, default=0.0)
    ad_frequency_level: Mapped[AdFrequencyLevel] = mapped_column(
        Enum(AdFrequencyLevel), default=AdFrequencyLevel.normal
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_active_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    products = relationship("Product", back_populates="merchant")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    behaviors = relationship("UserBehavior", back_populates="user")
