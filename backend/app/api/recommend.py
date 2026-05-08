from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


@router.get("/home", response_model=List[ProductResponse])
def home(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    products = db.query(Product).order_by(Product.sales_count.desc()).limit(20).all()
    return products


@router.get("/similar/{product_id}", response_model=List[ProductResponse])
def similar(product_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return []
    similar_products = db.query(Product).filter(
        Product.category_id == product.category_id,
        Product.id != product_id,
    ).limit(10).all()
    return similar_products


@router.get("/for-you", response_model=List[ProductResponse])
def for_you(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    products = db.query(Product).order_by(Product.created_at.desc()).limit(20).all()
    return products
