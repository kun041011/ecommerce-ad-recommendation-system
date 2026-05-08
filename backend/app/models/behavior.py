import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BehaviorType(str, enum.Enum):
    view = "view"
    click = "click"
    cart = "cart"
    purchase = "purchase"
    review = "review"
    search = "search"
    login = "login"


class UserBehavior(Base):
    __tablename__ = "user_behaviors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id"), nullable=True)
    behavior_type: Mapped[BehaviorType] = mapped_column(Enum(BehaviorType))
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="behaviors")
    product = relationship("Product")
