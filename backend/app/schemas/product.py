from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price: float
    category_id: int
    stock: int = 0
    tags: Optional[List[str]] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    tags: Optional[List[str]] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category_id: int
    merchant_id: int
    stock: int
    sales_count: int
    tags: Optional[List[str]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductSearchQuery(BaseModel):
    query: str = ""
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    page: int = 1
    page_size: int = 20
