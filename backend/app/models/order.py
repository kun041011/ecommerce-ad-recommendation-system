"""订单数据模型

定义订单表和订单明细表的ORM映射，记录用户的购买交易信息。
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    pending = "pending"        # 待付款
    paid = "paid"              # 已付款
    shipped = "shipped"        # 已发货
    completed = "completed"    # 已完成
    cancelled = "cancelled"    # 已取消


class Order(Base):
    """订单表ORM模型"""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # 订单ID，自增主键
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # 下单用户ID
    total_amount: Mapped[float] = mapped_column(Float)  # 订单总金额
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.pending)  # 订单状态，默认待付款
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 下单时间

    # ---- 关系映射 ----
    user = relationship("User", back_populates="orders")       # 下单用户
    items = relationship("OrderItem", back_populates="order")   # 订单明细列表


class OrderItem(Base):
    """订单明细表ORM模型，记录每个订单中包含的商品及数量"""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # 明细ID，自增主键
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"))  # 所属订单ID
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))  # 商品ID
    quantity: Mapped[int] = mapped_column(Integer)  # 购买数量
    price: Mapped[float] = mapped_column(Float)  # 下单时的商品单价（快照）

    # ---- 关系映射 ----
    order = relationship("Order", back_populates="items")  # 所属订单
    product = relationship("Product")                      # 对应商品
