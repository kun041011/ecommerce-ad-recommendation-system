from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.product import Product


def create_order(db: Session, user_id: int, items: list) -> Order:
    total = 0.0
    order_items = []
    for item_data in items:
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item_data['product_id']} not found")
        if product.stock < item_data["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        line_total = round(product.price * item_data["quantity"], 2)
        total += line_total
        order_items.append({"product": product, "quantity": item_data["quantity"], "price": product.price})

    order = Order(user_id=user_id, total_amount=round(total, 2))
    db.add(order)
    db.flush()
    for oi in order_items:
        db.add(OrderItem(order_id=order.id, product_id=oi["product"].id, quantity=oi["quantity"], price=oi["price"]))
        oi["product"].stock -= oi["quantity"]
        oi["product"].sales_count += oi["quantity"]
    db.commit()
    db.refresh(order)
    return order


def get_user_orders(db: Session, user_id: int) -> list:
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()


def get_order(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()
