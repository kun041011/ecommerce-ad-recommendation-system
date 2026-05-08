from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.product import Product


def create_product(db: Session, merchant_id: int, **kwargs) -> Product:
    product = Product(merchant_id=merchant_id, **kwargs)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def list_products(db: Session, page: int = 1, page_size: int = 20) -> dict:
    query = db.query(Product)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def search_products(
    db: Session, query: str = "", category_id: Optional[int] = None,
    min_price: Optional[float] = None, max_price: Optional[float] = None,
    page: int = 1, page_size: int = 20,
) -> dict:
    q = db.query(Product)
    if query:
        q = q.filter(or_(Product.name.contains(query), Product.description.contains(query)))
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def update_product(db: Session, product: Product, **kwargs) -> Product:
    for key, value in kwargs.items():
        if value is not None:
            setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product
