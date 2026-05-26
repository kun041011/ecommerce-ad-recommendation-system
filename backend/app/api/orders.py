"""订单路由模块

提供订单创建、用户订单列表查询和单个订单详情查询的REST API接口。
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import create_order, get_order, get_user_orders

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create(data: OrderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """创建订单接口

    参数:
        data: 订单数据，包含商品列表及数量
        db: 数据库会话
        user: 当前登录用户

    返回:
        Order: 创建成功的订单信息
    """
    # 将订单项Schema转换为字典列表
    items = [item.dict() for item in data.items]
    return create_order(db, user.id, items)


@router.get("", response_model=List[OrderResponse])
def list_mine(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """获取当前用户的订单列表

    参数:
        db: 数据库会话
        user: 当前登录用户

    返回:
        list[Order]: 当前用户的所有订单，按时间倒序
    """
    return get_user_orders(db, user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_by_id(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """根据ID获取订单详情（仅限本人订单）

    参数:
        order_id: 订单ID
        db: 数据库会话
        user: 当前登录用户

    返回:
        Order: 订单详细信息
    """
    order = get_order(db, order_id)
    # 校验订单存在且属于当前用户
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
