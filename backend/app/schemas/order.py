"""订单Pydantic模式

定义订单相关的请求/响应数据校验模式，包括下单请求和订单详情返回。
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    """订单明细创建模式（单个商品项）"""
    product_id: int   # 商品ID
    quantity: int      # 购买数量


class OrderCreate(BaseModel):
    """下单请求模式，包含一个或多个商品项"""
    items: List[OrderItemCreate]  # 订单商品列表


class OrderItemResponse(BaseModel):
    """订单明细响应模式"""
    id: int            # 明细ID
    product_id: int    # 商品ID
    quantity: int      # 购买数量
    price: float       # 下单时的商品单价（快照）

    model_config = {"from_attributes": True}  # 允许从ORM模型属性构造


class OrderResponse(BaseModel):
    """订单信息响应模式"""
    id: int                                    # 订单ID
    user_id: int                               # 下单用户ID
    total_amount: float                        # 订单总金额
    status: OrderStatus                        # 订单状态
    items: List[OrderItemResponse] = []        # 订单明细列表
    created_at: datetime                       # 下单时间

    model_config = {"from_attributes": True}   # 允许从ORM模型属性构造
