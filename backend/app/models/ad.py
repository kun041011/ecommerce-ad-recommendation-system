import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BidType(str, enum.Enum):
    CPC = "CPC"
    CPM = "CPM"


class AdStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    exhausted = "exhausted"


class ImpressionType(str, enum.Enum):
    show = "show"
    click = "click"
    convert = "convert"


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    advertiser_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(255), default="")
    target_url: Mapped[str] = mapped_column(String(255), default="")
    bid_amount: Mapped[float] = mapped_column(Float)
    bid_type: Mapped[BidType] = mapped_column(Enum(BidType), default=BidType.CPC)
    daily_budget: Mapped[float] = mapped_column(Float)
    total_budget: Mapped[float] = mapped_column(Float)
    spent_amount: Mapped[float] = mapped_column(Float, default=0.0)
    target_tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[AdStatus] = mapped_column(Enum(AdStatus), default=AdStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    advertiser = relationship("User")
    impressions = relationship("AdImpression", back_populates="ad")


class AdImpression(Base):
    __tablename__ = "ad_impressions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ad_id: Mapped[int] = mapped_column(Integer, ForeignKey("ads.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    impression_type: Mapped[ImpressionType] = mapped_column(Enum(ImpressionType))
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ad = relationship("Ad", back_populates="impressions")
    user = relationship("User")
