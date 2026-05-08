from typing import Optional, List, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_merchant
from app.database import get_db
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import (
    create_product, get_product, list_products, search_products, update_product,
)

router = APIRouter(prefix="/api/products", tags=["products"])


def _serialize_paginated(result: dict) -> dict:
    return {
        "items": [ProductResponse.from_orm(p) for p in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    }


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create(data: ProductCreate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    product = create_product(db, merchant_id=user.id, **data.dict())
    return product


@router.get("")
def list_all(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return _serialize_paginated(list_products(db, page, page_size))


@router.get("/search")
def search(
    query: str = "", category_id: Optional[int] = None,
    min_price: Optional[float] = None, max_price: Optional[float] = None,
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return _serialize_paginated(search_products(db, query, category_id, min_price, max_price, page, page_size))


@router.get("/{product_id}", response_model=ProductResponse)
def get_by_id(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    product = get_product(db, product_id)
    if not product or product.merchant_id != user.id:
        raise HTTPException(status_code=404, detail="Product not found")
    return update_product(db, product, **data.dict(exclude_unset=True))
