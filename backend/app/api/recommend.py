"""推荐路由模块

提供首页推荐、相似商品推荐和个性化推荐的REST API接口。
基于销量排序、分类关联和时间排序实现推荐逻辑。
"""

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
    """首页推荐接口

    按销量降序返回热门商品，作为首页默认推荐内容。

    参数:
        db: 数据库会话
        user: 当前登录用户

    返回:
        list[Product]: 按销量排序的前20个商品
    """
    # 按销量降序排列，取前20个热门商品
    products = db.query(Product).order_by(Product.sales_count.desc()).limit(20).all()
    return products


@router.get("/similar/{product_id}", response_model=List[ProductResponse])
def similar(product_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    """相似商品推荐接口

    根据目标商品的分类，推荐同分类下的其他商品。

    参数:
        product_id: 目标商品ID
        db: 数据库会话
        _user: 当前登录用户（用于登录校验）

    返回:
        list[Product]: 同分类下的相似商品列表（最多10个）
    """
    # 查找目标商品
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return []
    # 查找同分类下的其他商品
    similar_products = db.query(Product).filter(
        Product.category_id == product.category_id,
        Product.id != product_id,
    ).limit(10).all()
    return similar_products


@router.get("/for-you", response_model=List[ProductResponse])
def for_you(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """个性化推荐接口（猜你喜欢）

    当前实现为按创建时间倒序返回最新商品，
    后续可接入协同过滤等个性化推荐算法。

    参数:
        db: 数据库会话
        user: 当前登录用户

    返回:
        list[Product]: 按时间倒序的最新20个商品
    """
    # 按创建时间倒序，取最新的20个商品
    products = db.query(Product).order_by(Product.created_at.desc()).limit(20).all()
    return products
