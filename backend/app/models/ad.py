"""广告数据模型

定义广告表和广告曝光记录表的ORM映射，支持CPC/CPM竞价、预算控制和效果追踪。
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BidType(str, enum.Enum):
    """竞价类型枚举"""
    CPC = "CPC"  # 按点击付费（Cost Per Click）
    CPM = "CPM"  # 按千次曝光付费（Cost Per Mille）


class AdStatus(str, enum.Enum):
    """广告状态枚举"""
    active = "active"        # 投放中
    paused = "paused"        # 已暂停
    exhausted = "exhausted"  # 预算耗尽


class ImpressionType(str, enum.Enum):
    """广告曝光事件类型枚举"""
    show = "show"          # 展示（曝光）
    click = "click"        # 点击
    convert = "convert"    # 转化（如下单、注册）


class Ad(Base):
    """广告表ORM模型"""
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # 广告ID，自增主键
    advertiser_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # 广告主（商家）用户ID
    title: Mapped[str] = mapped_column(String(200))  # 广告标题
    content: Mapped[str] = mapped_column(Text, default="")  # 广告文案内容
    image_url: Mapped[str] = mapped_column(String(255), default="")  # 广告图片URL
    target_url: Mapped[str] = mapped_column(String(255), default="")  # 点击跳转目标URL
    bid_amount: Mapped[float] = mapped_column(Float)  # 单次竞价金额（CPC为单次点击价，CPM为千次曝光价）
    bid_type: Mapped[BidType] = mapped_column(Enum(BidType), default=BidType.CPC)  # 竞价类型
    daily_budget: Mapped[float] = mapped_column(Float)  # 每日预算上限
    total_budget: Mapped[float] = mapped_column(Float)  # 总预算上限
    spent_amount: Mapped[float] = mapped_column(Float, default=0.0)  # 已消耗金额
    target_tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # 定向标签（JSON数组），匹配用户兴趣
    status: Mapped[AdStatus] = mapped_column(Enum(AdStatus), default=AdStatus.active)  # 广告状态
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 广告创建时间

    # ---- 关系映射 ----
    advertiser = relationship("User")  # 广告主
    impressions = relationship("AdImpression", back_populates="ad")  # 曝光记录列表


class AdImpression(Base):
    """广告曝光记录表ORM模型，记录每次展示、点击、转化事件"""
    __tablename__ = "ad_impressions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # 记录ID，自增主键
    ad_id: Mapped[int] = mapped_column(Integer, ForeignKey("ads.id"))  # 关联广告ID
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # 触发用户ID
    impression_type: Mapped[ImpressionType] = mapped_column(Enum(ImpressionType))  # 事件类型（展示/点击/转化）
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # 事件上下文（如页面来源、设备信息等）
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 事件发生时间

    # ---- 关系映射 ----
    ad = relationship("Ad", back_populates="impressions")  # 关联广告
    user = relationship("User")  # 触发用户
