"""商品路由模块

提供商品的创建、查询、搜索和更新的REST API接口。
支持分页查询和多条件筛选搜索。
"""

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
    """将分页查询结果序列化为响应格式

    参数:
        result: 包含items、total、page、page_size的分页数据字典

    返回:
        dict: 序列化后的分页响应，items中每项转为ProductResponse
    """
    return {
        "items": [ProductResponse.from_orm(p) for p in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    }


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create(data: ProductCreate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    """创建商品接口（仅商家可用）

    参数:
        data: 商品信息（名称、价格、库存等）
        db: 数据库会话
        user: 当前商家用户（需商家权限）

    返回:
        Product: 创建成功的商品信息
    """
    product = create_product(db, merchant_id=user.id, **data.dict())
    return product


@router.get("")
def list_all(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """获取商品列表（分页）

    参数:
        page: 页码，从1开始
        page_size: 每页数量，范围1-100
        db: 数据库会话

    返回:
        dict: 分页商品列表，包含items、total、page、page_size
    """
    return _serialize_paginated(list_products(db, page, page_size))


@router.get("/search")
def search(
    query: str = "", category_id: Optional[int] = None,
    min_price: Optional[float] = None, max_price: Optional[float] = None,
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """商品搜索接口（支持关键词、分类、价格区间过滤）

    参数:
        query: 搜索关键词（匹配商品名称或描述）
        category_id: 分类ID筛选
        min_price: 最低价格
        max_price: 最高价格
        page: 页码
        page_size: 每页数量
        db: 数据库会话

    返回:
        dict: 符合条件的分页商品列表
    """
    return _serialize_paginated(search_products(db, query, category_id, min_price, max_price, page, page_size))


@router.get("/{product_id}", response_model=ProductResponse)
def get_by_id(product_id: int, db: Session = Depends(get_db)):
    """根据ID获取商品详情

    参数:
        product_id: 商品ID
        db: 数据库会话

    返回:
        Product: 商品详细信息
    """
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    """更新商品信息（仅商品所属商家可操作）

    参数:
        product_id: 商品ID
        data: 需要更新的商品字段
        db: 数据库会话
        user: 当前商家用户（需商家权限）

    返回:
        Product: 更新后的商品信息
    """
    # 校验商品存在且属于当前商家
    product = get_product(db, product_id)
    if not product or product.merchant_id != user.id:
        raise HTTPException(status_code=404, detail="Product not found")
    return update_product(db, product, **data.dict(exclude_unset=True))
