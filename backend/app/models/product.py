"""商品数据模型

定义商品表和分类表的ORM映射，支持多级分类、标签筛选和向量嵌入存储。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    """商品分类表ORM模型，支持父子层级结构"""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # 分类ID，自增主键
    name: Mapped[str] = mapped_column(String(50))  # 分类名称
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)  # 父分类ID，顶级分类为空

    # ---- 关系映射 ----
    children = relationship("Category", back_populates="parent")  # 子分类列表
    parent = relationship("Category", back_populates="children", remote_side="Category.id")  # 父分类
    products = relationship("Product", back_populates="category")  # 该分类下的商品列表


class Product(Base):
    """商品表ORM模型"""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  # 商品ID，自增主键
    name: Mapped[str] = mapped_column(String(200))  # 商品名称
    description: Mapped[str] = mapped_column(Text, default="")  # 商品描述
    price: Mapped[float] = mapped_column(Float)  # 商品单价
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))  # 所属分类ID
    merchant_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # 发布商家的用户ID
    stock: Mapped[int] = mapped_column(Integer, default=0)  # 库存数量
    sales_count: Mapped[int] = mapped_column(Integer, default=0)  # 累计销量
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # 商品标签（JSON数组），用于广告定向和推荐
    embedding: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)  # 商品向量嵌入，用于相似度推荐
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 商品创建时间

    # ---- 关系映射 ----
    category = relationship("Category", back_populates="products")  # 所属分类
    merchant = relationship("User", back_populates="products")      # 发布商家
    reviews = relationship("Review", back_populates="product")      # 商品评价列表
