"""商品Pydantic模式

定义商品和分类相关的请求/响应数据校验模式，包括商品的创建、更新、查询和搜索。
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    """商品分类响应模式"""
    id: int                            # 分类ID
    name: str                          # 分类名称
    parent_id: Optional[int] = None    # 父分类ID，顶级分类为空

    model_config = {"from_attributes": True}  # 允许从ORM模型属性构造


class ProductCreate(BaseModel):
    """商品创建请求模式（商家使用）"""
    name: str                              # 商品名称
    description: str = ""                  # 商品描述
    price: float                           # 商品单价
    category_id: int                       # 所属分类ID
    stock: int = 0                         # 初始库存数量
    tags: Optional[List[str]] = None       # 商品标签列表


class ProductUpdate(BaseModel):
    """商品更新请求模式，所有字段可选"""
    name: Optional[str] = None             # 商品名称
    description: Optional[str] = None      # 商品描述
    price: Optional[float] = None          # 商品单价
    stock: Optional[int] = None            # 库存数量
    tags: Optional[List[str]] = None       # 商品标签列表


class ProductResponse(BaseModel):
    """商品信息响应模式"""
    id: int                                # 商品ID
    name: str                              # 商品名称
    description: str                       # 商品描述
    price: float                           # 商品单价
    category_id: int                       # 所属分类ID
    merchant_id: int                       # 发布商家ID
    stock: int                             # 当前库存
    sales_count: int                       # 累计销量
    tags: Optional[List[str]] = None       # 商品标签列表
    created_at: datetime                   # 商品创建时间

    model_config = {"from_attributes": True}  # 允许从ORM模型属性构造


class ProductSearchQuery(BaseModel):
    """商品搜索查询模式，支持关键词、分类和价格区间筛选"""
    query: str = ""                        # 搜索关键词
    category_id: Optional[int] = None      # 按分类筛选
    min_price: Optional[float] = None      # 最低价格
    max_price: Optional[float] = None      # 最高价格
    page: int = 1                          # 页码，从1开始
    page_size: int = 20                    # 每页数量
