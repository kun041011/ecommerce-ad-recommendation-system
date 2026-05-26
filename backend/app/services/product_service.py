"""商品服务模块

提供商品的创建、查询、搜索和更新等数据库操作。
支持按关键词、分类、价格区间的多条件组合搜索。
"""

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.product import Product


def create_product(db: Session, merchant_id: int, **kwargs) -> Product:
    """创建商品

    参数:
        db: 数据库会话
        merchant_id: 商家用户ID
        **kwargs: 商品属性（name、price、stock等）

    返回:
        Product: 创建成功的商品对象
    """
    product = Product(merchant_id=merchant_id, **kwargs)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """根据ID查询单个商品

    参数:
        db: 数据库会话
        product_id: 商品ID

    返回:
        Optional[Product]: 商品对象，不存在则返回None
    """
    return db.query(Product).filter(Product.id == product_id).first()


def list_products(db: Session, page: int = 1, page_size: int = 20) -> dict:
    """分页获取商品列表

    参数:
        db: 数据库会话
        page: 页码，从1开始
        page_size: 每页数量

    返回:
        dict: 包含items（商品列表）、total（总数）、page、page_size的分页数据
    """
    query = db.query(Product)
    total = query.count()
    # 计算偏移量并分页查询
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def search_products(
    db: Session, query: str = "", category_id: Optional[int] = None,
    min_price: Optional[float] = None, max_price: Optional[float] = None,
    page: int = 1, page_size: int = 20,
) -> dict:
    """多条件搜索商品

    支持关键词模糊搜索（名称或描述）、分类过滤和价格区间过滤。

    参数:
        db: 数据库会话
        query: 搜索关键词（模糊匹配名称和描述）
        category_id: 分类ID过滤
        min_price: 最低价格过滤
        max_price: 最高价格过滤
        page: 页码
        page_size: 每页数量

    返回:
        dict: 符合条件的分页商品数据
    """
    q = db.query(Product)
    # 关键词模糊搜索：匹配名称或描述
    if query:
        q = q.filter(or_(Product.name.contains(query), Product.description.contains(query)))
    # 按分类ID过滤
    if category_id:
        q = q.filter(Product.category_id == category_id)
    # 按最低价格过滤
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    # 按最高价格过滤
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def update_product(db: Session, product: Product, **kwargs) -> Product:
    """更新商品信息

    仅更新传入的非None字段。

    参数:
        db: 数据库会话
        product: 待更新的商品对象
        **kwargs: 需要更新的字段及其新值

    返回:
        Product: 更新后的商品对象
    """
    # 遍历参数，仅更新非None的字段
    for key, value in kwargs.items():
        if value is not None:
            setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product
