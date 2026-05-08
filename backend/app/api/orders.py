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
    items = [item.dict() for item in data.items]
    return create_order(db, user.id, items)


@router.get("", response_model=List[OrderResponse])
def list_mine(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_user_orders(db, user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_by_id(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = get_order(db, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
