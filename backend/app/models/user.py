"""用户数据模型

定义用户表的ORM映射，包含认证信息、角色权限、活跃度评分和广告频控等级等字段。
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    consumer = "consumer"    # 普通消费者
    merchant = "merchant"    # 商家（可发布商品和广告）
    admin = "admin"          # 管理员


class AdFrequencyLevel(str, enum.Enum):
    """广告投放频率等级枚举，由活跃度评分自动计算"""
    low = "low"        # 低频：活跃度较低的用户，减少广告打扰
    normal = "normal"  # 正常频率
    high = "high"      # 高频：高活跃用户，可接受更多广告


class User(Base):
    """用户表ORM模型"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # 用户ID，自增主键
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # 用户名，唯一约束
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)  # 邮箱，唯一约束
    hashed_password: Mapped[str] = mapped_column(String(255))  # 哈希后的密码
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # 头像URL，可为空
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.consumer)  # 用户角色，默认为消费者
    activity_score: Mapped[float] = mapped_column(Float, default=0.0)  # 活跃度评分（0-100），供频控组件读取
    ad_frequency_level: Mapped[AdFrequencyLevel] = mapped_column(
        Enum(AdFrequencyLevel), default=AdFrequencyLevel.normal
    )  # 广告频控等级，根据活跃度自动调整
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 注册时间
    last_active_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 最后活跃时间

    # ---- 关系映射 ----
    products = relationship("Product", back_populates="merchant")      # 商家发布的商品列表
    orders = relationship("Order", back_populates="user")              # 用户的订单列表
    reviews = relationship("Review", back_populates="user")            # 用户发表的评价列表
    behaviors = relationship("UserBehavior", back_populates="user")    # 用户行为日志列表
