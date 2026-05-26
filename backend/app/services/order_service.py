"""订单服务模块

提供订单创建、查询等数据库操作。
创建订单时自动校验库存、计算金额、扣减库存并更新销量。
"""

from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.product import Product


def create_order(db: Session, user_id: int, items: list) -> Order:
    """创建订单

    校验每个商品的存在性和库存充足性，计算订单总金额，
    创建订单和订单项，并扣减对应商品库存、更新销量。

    参数:
        db: 数据库会话
        user_id: 下单用户ID
        items: 订单项列表，每项包含product_id和quantity

    返回:
        Order: 创建成功的订单对象

    异常:
        HTTPException: 商品不存在（400）或库存不足（400）
    """
    total = 0.0
    order_items = []
    for item_data in items:
        # 查询商品是否存在
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item_data['product_id']} not found")
        # 校验库存是否充足
        if product.stock < item_data["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        # 计算单行金额并累加到订单总额
        line_total = round(product.price * item_data["quantity"], 2)
        total += line_total
        order_items.append({"product": product, "quantity": item_data["quantity"], "price": product.price})

    # 创建订单主记录
    order = Order(user_id=user_id, total_amount=round(total, 2))
    db.add(order)
    db.flush()  # 刷新获取order.id，但不提交事务
    # 创建订单项并扣减库存、更新销量
    for oi in order_items:
        db.add(OrderItem(order_id=order.id, product_id=oi["product"].id, quantity=oi["quantity"], price=oi["price"]))
        oi["product"].stock -= oi["quantity"]       # 扣减库存
        oi["product"].sales_count += oi["quantity"]  # 更新销量
    db.commit()
    db.refresh(order)
    return order


def get_user_orders(db: Session, user_id: int) -> list:
    """获取指定用户的所有订单

    参数:
        db: 数据库会话
        user_id: 用户ID

    返回:
        list[Order]: 该用户的所有订单，按创建时间倒序排列
    """
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """根据ID查询单个订单

    参数:
        db: 数据库会话
        order_id: 订单ID

    返回:
        Optional[Order]: 订单对象，不存在则返回None
    """
    return db.query(Order).filter(Order.id == order_id).first()
