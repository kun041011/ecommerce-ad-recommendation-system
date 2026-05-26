"""社区数据模型（评价、问答）

定义商品评价表和商品问答表的ORM映射，支持用户对商品的评分评论和互动问答。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Review(Base):
    """商品评价表ORM模型"""
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # 评价ID，自增主键
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # 评价用户ID
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))  # 被评价的商品ID
    rating: Mapped[int] = mapped_column(Integer)  # 评分（1-5星）
    content: Mapped[str] = mapped_column(Text, default="")  # 评价文字内容
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)  # "有帮助"投票数
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 评价发布时间

    # ---- 关系映射 ----
    user = relationship("User", back_populates="reviews")        # 评价用户
    product = relationship("Product", back_populates="reviews")  # 被评价商品


class QA(Base):
    """商品问答表ORM模型，支持用户提问、商家或其他用户回答"""
    __tablename__ = "qa"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # 问答ID，自增主键
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))  # 关联商品ID
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # 提问用户ID
    question: Mapped[str] = mapped_column(Text)  # 问题内容
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 回答内容，未回答时为空
    answered_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # 回答者用户ID
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 提问时间

    # ---- 关系映射 ----
    questioner = relationship("User", foreign_keys=[user_id])      # 提问者
    answerer = relationship("User", foreign_keys=[answered_by])    # 回答者
    product = relationship("Product")                              # 关联商品
