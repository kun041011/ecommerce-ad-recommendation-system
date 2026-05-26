"""行为日志数据模型

定义用户行为日志表的ORM映射，记录浏览、点击、加购、购买、搜索等行为，
供推荐算法（UserCF）和活跃度评分系统使用。
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BehaviorType(str, enum.Enum):
    """用户行为类型枚举"""
    view = "view"          # 浏览商品
    click = "click"        # 点击商品
    cart = "cart"           # 加入购物车
    purchase = "purchase"  # 购买商品
    review = "review"      # 发表评价
    search = "search"      # 搜索
    login = "login"        # 登录


class UserBehavior(Base):
    """用户行为日志表ORM模型，记录用户在平台上的各类交互行为"""
    __tablename__ = "user_behaviors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # 行为记录ID，自增主键
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # 行为用户ID
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id"), nullable=True)  # 关联商品ID（搜索、登录等行为可为空）
    behavior_type: Mapped[BehaviorType] = mapped_column(Enum(BehaviorType))  # 行为类型
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # 行为上下文（如搜索关键词、页面来源等）
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 行为发生时间

    # ---- 关系映射 ----
    user = relationship("User", back_populates="behaviors")  # 行为用户
    product = relationship("Product")                        # 关联商品
