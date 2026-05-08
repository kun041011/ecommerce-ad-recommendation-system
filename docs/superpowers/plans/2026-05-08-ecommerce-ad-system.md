# E-Commerce Ad Recommendation System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete e-commerce advertising recommendation system with collaborative filtering, deep learning ranking, community-driven frequency control, and activity-based ad adjustment.

**Architecture:** Single-process FastAPI application with modular code separation. SQLite for persistence, Redis for caching/counters. Multi-stage recommendation pipeline (recall → ranking → rerank). Vue 3 SPA frontend.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, PyTorch, scikit-learn, Redis, Vue 3, Element Plus, Pinia, Vite

---

## Phase 1: Foundation

### Task 1: Project Scaffold and Dependencies

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Create backend directory structure**

```bash
mkdir -p backend/app/models backend/app/schemas backend/app/api backend/app/services
mkdir -p backend/app/recommendation/recall backend/app/recommendation/ranking backend/app/recommendation/rerank
mkdir -p backend/app/ad_engine backend/app/activity
mkdir -p backend/tests/test_recommendation backend/tests/test_ad_engine backend/tests/test_activity backend/tests/test_api
mkdir -p backend/scripts data
touch backend/app/__init__.py backend/app/models/__init__.py backend/app/schemas/__init__.py
touch backend/app/api/__init__.py backend/app/services/__init__.py
touch backend/app/recommendation/__init__.py backend/app/recommendation/recall/__init__.py
touch backend/app/recommendation/ranking/__init__.py backend/app/recommendation/rerank/__init__.py
touch backend/app/ad_engine/__init__.py backend/app/activity/__init__.py
touch backend/tests/__init__.py backend/tests/test_recommendation/__init__.py
touch backend/tests/test_ad_engine/__init__.py backend/tests/test_activity/__init__.py
touch backend/tests/test_api/__init__.py
```

- [ ] **Step 2: Create requirements.txt**

Create `backend/requirements.txt`:
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
pydantic==2.9.0
pydantic-settings==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
httpx==0.27.0
redis==5.1.0
fakeredis==2.24.0
scikit-learn==1.5.2
numpy==1.26.4
scipy==1.14.0
torch==2.4.0
pytest==8.3.0
pytest-asyncio==0.24.0
```

- [ ] **Step 3: Create config.py**

Create `backend/app/config.py`:
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/ecommerce.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ACTIVITY_DECAY_LAMBDA: float = 0.1
    ACTIVITY_UPDATE_INTERVAL_SECONDS: int = 3600

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 4: Create database.py**

Create `backend/app/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: Create main.py**

Create `backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce Ad Recommendation System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 6: Create test conftest.py**

Create `backend/tests/conftest.py`:
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./data/test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

- [ ] **Step 7: Write test for health endpoint**

Create `backend/tests/test_api/test_health.py`:
```python
def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 8: Run test**

```bash
cd backend && python -m pytest tests/test_api/test_health.py -v
```

Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add backend/ data/
git commit -m "feat: project scaffold with FastAPI, SQLAlchemy, pytest"
```

---

### Task 2: Database Models

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/product.py`
- Create: `backend/app/models/order.py`
- Create: `backend/app/models/ad.py`
- Create: `backend/app/models/community.py`
- Create: `backend/app/models/behavior.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_api/test_models.py`

- [ ] **Step 1: Create user model**

Create `backend/app/models/user.py`:
```python
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    consumer = "consumer"
    merchant = "merchant"
    admin = "admin"


class AdFrequencyLevel(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.consumer)
    activity_score: Mapped[float] = mapped_column(Float, default=0.0)
    ad_frequency_level: Mapped[AdFrequencyLevel] = mapped_column(
        Enum(AdFrequencyLevel), default=AdFrequencyLevel.normal
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_active_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    products = relationship("Product", back_populates="merchant")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    behaviors = relationship("UserBehavior", back_populates="user")
```

- [ ] **Step 2: Create product and category models**

Create `backend/app/models/product.py`:
```python
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)

    children = relationship("Category", back_populates="parent")
    parent = relationship("Category", back_populates="children", remote_side="Category.id")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Float)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    merchant_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    sales_count: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    category = relationship("Category", back_populates="products")
    merchant = relationship("User", back_populates="products")
    reviews = relationship("Review", back_populates="product")
```

- [ ] **Step 3: Create order models**

Create `backend/app/models/order.py`:
```python
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    completed = "completed"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    total_amount: Mapped[float] = mapped_column(Float)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
```

- [ ] **Step 4: Create ad models**

Create `backend/app/models/ad.py`:
```python
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BidType(str, enum.Enum):
    CPC = "CPC"
    CPM = "CPM"


class AdStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    exhausted = "exhausted"


class ImpressionType(str, enum.Enum):
    show = "show"
    click = "click"
    convert = "convert"


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    advertiser_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(255), default="")
    target_url: Mapped[str] = mapped_column(String(255), default="")
    bid_amount: Mapped[float] = mapped_column(Float)
    bid_type: Mapped[BidType] = mapped_column(Enum(BidType), default=BidType.CPC)
    daily_budget: Mapped[float] = mapped_column(Float)
    total_budget: Mapped[float] = mapped_column(Float)
    spent_amount: Mapped[float] = mapped_column(Float, default=0.0)
    target_tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[AdStatus] = mapped_column(Enum(AdStatus), default=AdStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    advertiser = relationship("User")
    impressions = relationship("AdImpression", back_populates="ad")


class AdImpression(Base):
    __tablename__ = "ad_impressions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ad_id: Mapped[int] = mapped_column(Integer, ForeignKey("ads.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    impression_type: Mapped[ImpressionType] = mapped_column(Enum(ImpressionType))
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ad = relationship("Ad", back_populates="impressions")
    user = relationship("User")
```

- [ ] **Step 5: Create community models**

Create `backend/app/models/community.py`:
```python
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    rating: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text, default="")
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")


class QA(Base):
    __tablename__ = "qa"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    questioner = relationship("User", foreign_keys=[user_id])
    answerer = relationship("User", foreign_keys=[answered_by])
    product = relationship("Product")
```

- [ ] **Step 6: Create behavior model**

Create `backend/app/models/behavior.py`:
```python
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BehaviorType(str, enum.Enum):
    view = "view"
    click = "click"
    cart = "cart"
    purchase = "purchase"
    review = "review"
    search = "search"
    login = "login"


class UserBehavior(Base):
    __tablename__ = "user_behaviors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    product_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("products.id"), nullable=True)
    behavior_type: Mapped[BehaviorType] = mapped_column(Enum(BehaviorType))
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="behaviors")
    product = relationship("Product")
```

- [ ] **Step 7: Update models __init__.py**

Create `backend/app/models/__init__.py`:
```python
from app.models.ad import Ad, AdImpression, AdStatus, BidType, ImpressionType
from app.models.behavior import BehaviorType, UserBehavior
from app.models.community import QA, Review
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Category, Product
from app.models.user import AdFrequencyLevel, User, UserRole

__all__ = [
    "User", "UserRole", "AdFrequencyLevel",
    "Product", "Category",
    "Order", "OrderItem", "OrderStatus",
    "Ad", "AdImpression", "AdStatus", "BidType", "ImpressionType",
    "Review", "QA",
    "UserBehavior", "BehaviorType",
]
```

- [ ] **Step 8: Write model creation test**

Create `backend/tests/test_api/test_models.py`:
```python
from app.models import User, Product, Category, Order, OrderItem, UserRole


def test_create_user(db):
    user = User(username="testuser", email="test@test.com", hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.id is not None
    assert user.role == UserRole.consumer
    assert user.activity_score == 0.0


def test_create_product_with_category(db):
    user = User(username="merchant1", email="m@test.com", hashed_password="hashed", role=UserRole.merchant)
    cat = Category(name="Electronics")
    db.add_all([user, cat])
    db.commit()

    product = Product(name="Phone", price=999.0, category_id=cat.id, merchant_id=user.id, stock=10)
    db.add(product)
    db.commit()
    db.refresh(product)
    assert product.id is not None
    assert product.category.name == "Electronics"


def test_create_order_with_items(db):
    user = User(username="buyer", email="b@test.com", hashed_password="hashed")
    cat = Category(name="Books")
    db.add_all([user, cat])
    db.commit()

    product = Product(name="Book", price=29.99, category_id=cat.id, merchant_id=user.id, stock=5)
    db.add(product)
    db.commit()

    order = Order(user_id=user.id, total_amount=29.99)
    db.add(order)
    db.commit()

    item = OrderItem(order_id=order.id, product_id=product.id, quantity=1, price=29.99)
    db.add(item)
    db.commit()

    db.refresh(order)
    assert len(order.items) == 1
    assert order.items[0].product.name == "Book"
```

- [ ] **Step 9: Run tests**

```bash
cd backend && python -m pytest tests/test_api/test_models.py -v
```

Expected: 3 tests PASS

- [ ] **Step 10: Commit**

```bash
git add backend/
git commit -m "feat: add all database models (user, product, order, ad, community, behavior)"
```

---

### Task 3: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/product.py`
- Create: `backend/app/schemas/order.py`
- Create: `backend/app/schemas/ad.py`
- Create: `backend/app/schemas/community.py`
- Modify: `backend/app/schemas/__init__.py`

- [ ] **Step 1: Create user schemas**

Create `backend/app/schemas/user.py`:
```python
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import AdFrequencyLevel, UserRole


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: str | None = None
    role: UserRole
    activity_score: float
    ad_frequency_level: AdFrequencyLevel
    created_at: datetime
    last_active_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

- [ ] **Step 2: Create product schemas**

Create `backend/app/schemas/product.py`:
```python
from datetime import datetime

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None = None

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price: float
    category_id: int
    stock: int = 0
    tags: list[str] | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    tags: list[str] | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category_id: int
    merchant_id: int
    stock: int
    sales_count: int
    tags: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductSearchQuery(BaseModel):
    query: str = ""
    category_id: int | None = None
    min_price: float | None = None
    max_price: float | None = None
    page: int = 1
    page_size: int = 20
```

- [ ] **Step 3: Create order schemas**

Create `backend/app/schemas/order.py`:
```python
from datetime import datetime

from pydantic import BaseModel

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: OrderStatus
    items: list[OrderItemResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: Create ad schemas**

Create `backend/app/schemas/ad.py`:
```python
from datetime import datetime

from pydantic import BaseModel

from app.models.ad import AdStatus, BidType, ImpressionType


class AdCreate(BaseModel):
    title: str
    content: str = ""
    image_url: str = ""
    target_url: str = ""
    bid_amount: float
    bid_type: BidType = BidType.CPC
    daily_budget: float
    total_budget: float
    target_tags: list[str] | None = None


class AdResponse(BaseModel):
    id: int
    advertiser_id: int
    title: str
    content: str
    image_url: str
    target_url: str
    bid_amount: float
    bid_type: BidType
    daily_budget: float
    total_budget: float
    spent_amount: float
    target_tags: list[str] | None = None
    status: AdStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class AdFetchResponse(BaseModel):
    ads: list[AdResponse]
    frequency_level: str
    remaining_today: int


class ImpressionCreate(BaseModel):
    ad_id: int
    impression_type: ImpressionType
    context: dict | None = None


class AdStatsResponse(BaseModel):
    ad_id: int
    total_shows: int
    total_clicks: int
    total_converts: int
    ctr: float
    spent: float
```

- [ ] **Step 5: Create community schemas**

Create `backend/app/schemas/community.py`:
```python
from datetime import datetime

from pydantic import BaseModel, field_validator


class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    content: str = ""

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    content: str
    helpful_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class QACreate(BaseModel):
    product_id: int
    question: str


class QAAnswerCreate(BaseModel):
    answer: str


class QAResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    question: str
    answer: str | None = None
    answered_by: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BehaviorTrack(BaseModel):
    product_id: int | None = None
    behavior_type: str
    context: dict | None = None


class ActivityScoreResponse(BaseModel):
    score: float
    level: str
    ad_frequency_level: str
```

- [ ] **Step 6: Update schemas __init__.py**

Create `backend/app/schemas/__init__.py`:
```python
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductSearchQuery, CategoryResponse,
)
from app.schemas.order import OrderCreate, OrderItemCreate, OrderResponse, OrderItemResponse
from app.schemas.ad import (
    AdCreate, AdResponse, AdFetchResponse,
    ImpressionCreate, AdStatsResponse,
)
from app.schemas.community import (
    ReviewCreate, ReviewResponse,
    QACreate, QAAnswerCreate, QAResponse,
    BehaviorTrack, ActivityScoreResponse,
)
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: add Pydantic request/response schemas for all modules"
```

---

### Task 4: Auth API (Register, Login, JWT)

**Files:**
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/auth.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_api/test_auth.py`

- [ ] **Step 1: Write failing auth tests**

Create `backend/tests/test_api/test_auth.py`:
```python
def test_register(client):
    response = client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert "id" in data


def test_register_duplicate_username(client):
    client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123"
    })
    response = client.post("/api/auth/register", json={
        "username": "alice", "email": "alice2@test.com", "password": "secret123"
    })
    assert response.status_code == 400


def test_login(client):
    client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123"
    })
    response = client.post("/api/auth/login", json={
        "username": "alice", "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123"
    })
    response = client.post("/api/auth/login", json={
        "username": "alice", "password": "wrong"
    })
    assert response.status_code == 401


def test_me(client):
    client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123"
    })
    login_resp = client.post("/api/auth/login", json={
        "username": "alice", "password": "secret123"
    })
    token = login_resp.json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "alice"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && python -m pytest tests/test_api/test_auth.py -v
```

Expected: FAIL (routes not defined)

- [ ] **Step 3: Create auth service**

Create `backend/app/services/auth_service.py`:
```python
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return int(payload["sub"])
    except Exception:
        return None


def register_user(db: Session, username: str, email: str, password: str) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
```

- [ ] **Step 4: Create dependency injection for current user**

Create `backend/app/api/deps.py`:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_merchant(user: User = Depends(get_current_user)) -> User:
    if user.role not in (UserRole.merchant, UserRole.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Merchant access required")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
```

- [ ] **Step 5: Create auth router**

Create `backend/app/api/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import authenticate_user, create_access_token, register_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    user = register_user(db, data.username, data.email, data.password)
    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
```

- [ ] **Step 6: Register auth router in main.py**

Replace the content of `backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce Ad Recommendation System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 7: Run auth tests**

```bash
cd backend && python -m pytest tests/test_api/test_auth.py -v
```

Expected: 5 tests PASS

- [ ] **Step 8: Commit**

```bash
git add backend/
git commit -m "feat: auth system with register, login, JWT, role-based access"
```

---

## Phase 2: Core E-Commerce

### Task 5: Product API (CRUD + Search)

**Files:**
- Create: `backend/app/services/product_service.py`
- Create: `backend/app/api/products.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_api/test_products.py`

- [ ] **Step 1: Write failing product tests**

Create `backend/tests/test_api/test_products.py`:
```python
import pytest


@pytest.fixture
def merchant_token(client):
    from app.models.user import UserRole
    client.post("/api/auth/register", json={
        "username": "merchant", "email": "m@test.com", "password": "secret123"
    })
    # Manually set role to merchant
    from app.database import get_db
    db = next(client.app.dependency_overrides[get_db]())
    from app.models import User
    user = db.query(User).filter(User.username == "merchant").first()
    user.role = UserRole.merchant
    db.commit()

    resp = client.post("/api/auth/login", json={"username": "merchant", "password": "secret123"})
    return resp.json()["access_token"]


@pytest.fixture
def setup_category(client):
    from app.database import get_db
    from app.models import Category
    db = next(client.app.dependency_overrides[get_db]())
    cat = Category(name="Electronics")
    db.add(cat)
    db.commit()
    return cat.id


def test_create_product(client, merchant_token, setup_category):
    response = client.post("/api/products", json={
        "name": "Laptop", "price": 1299.99, "category_id": setup_category,
        "stock": 50, "tags": ["laptop", "computer"]
    }, headers={"Authorization": f"Bearer {merchant_token}"})
    assert response.status_code == 201
    assert response.json()["name"] == "Laptop"


def test_list_products(client, merchant_token, setup_category):
    client.post("/api/products", json={
        "name": "Phone", "price": 999.0, "category_id": setup_category, "stock": 10
    }, headers={"Authorization": f"Bearer {merchant_token}"})
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_product(client, merchant_token, setup_category):
    resp = client.post("/api/products", json={
        "name": "Tablet", "price": 499.0, "category_id": setup_category, "stock": 5
    }, headers={"Authorization": f"Bearer {merchant_token}"})
    pid = resp.json()["id"]
    response = client.get(f"/api/products/{pid}")
    assert response.status_code == 200
    assert response.json()["name"] == "Tablet"


def test_search_products(client, merchant_token, setup_category):
    client.post("/api/products", json={
        "name": "Gaming Laptop", "price": 1999.0, "category_id": setup_category, "stock": 3
    }, headers={"Authorization": f"Bearer {merchant_token}"})
    response = client.get("/api/products/search", params={"query": "Gaming"})
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
```

- [ ] **Step 2: Create product service**

Create `backend/app/services/product_service.py`:
```python
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.product import Product


def create_product(db: Session, merchant_id: int, **kwargs) -> Product:
    product = Product(merchant_id=merchant_id, **kwargs)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def list_products(db: Session, page: int = 1, page_size: int = 20) -> dict:
    query = db.query(Product)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def search_products(
    db: Session, query: str = "", category_id: int | None = None,
    min_price: float | None = None, max_price: float | None = None,
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
```

- [ ] **Step 3: Create product router**

Create `backend/app/api/products.py`:
```python
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


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create(data: ProductCreate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    product = create_product(db, merchant_id=user.id, **data.model_dump())
    return product


@router.get("", response_model=dict)
def list_all(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return list_products(db, page, page_size)


@router.get("/search", response_model=dict)
def search(
    query: str = "", category_id: int | None = None,
    min_price: float | None = None, max_price: float | None = None,
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return search_products(db, query, category_id, min_price, max_price, page, page_size)


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
    return update_product(db, product, **data.model_dump(exclude_unset=True))
```

- [ ] **Step 4: Register router in main.py**

Add to `backend/app/main.py` imports and router registration:
```python
from app.api import auth, products
# ...
app.include_router(products.router)
```

- [ ] **Step 5: Run tests**

```bash
cd backend && python -m pytest tests/test_api/test_products.py -v
```

Expected: 4 tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat: product CRUD and search API"
```

---

### Task 6: Order API

**Files:**
- Create: `backend/app/services/order_service.py`
- Create: `backend/app/api/orders.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_api/test_orders.py`

- [ ] **Step 1: Write failing order tests**

Create `backend/tests/test_api/test_orders.py`:
```python
import pytest
from app.models import User, Category, Product, UserRole


@pytest.fixture
def user_token(client):
    client.post("/api/auth/register", json={
        "username": "buyer", "email": "buyer@test.com", "password": "secret123"
    })
    resp = client.post("/api/auth/login", json={"username": "buyer", "password": "secret123"})
    return resp.json()["access_token"]


@pytest.fixture
def product_id(db):
    user = User(username="seller", email="seller@t.com", hashed_password="h", role=UserRole.merchant)
    cat = Category(name="Toys")
    db.add_all([user, cat])
    db.commit()
    p = Product(name="Toy", price=19.99, category_id=cat.id, merchant_id=user.id, stock=10)
    db.add(p)
    db.commit()
    return p.id


def test_create_order(client, user_token, product_id):
    response = client.post("/api/orders", json={
        "items": [{"product_id": product_id, "quantity": 2}]
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["total_amount"] == 39.98
    assert len(data["items"]) == 1


def test_create_order_insufficient_stock(client, user_token, product_id):
    response = client.post("/api/orders", json={
        "items": [{"product_id": product_id, "quantity": 999}]
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 400


def test_list_orders(client, user_token, product_id):
    client.post("/api/orders", json={
        "items": [{"product_id": product_id, "quantity": 1}]
    }, headers={"Authorization": f"Bearer {user_token}"})
    response = client.get("/api/orders", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 1
```

- [ ] **Step 2: Create order service**

Create `backend/app/services/order_service.py`:
```python
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.product import Product


def create_order(db: Session, user_id: int, items: list[dict]) -> Order:
    total = 0.0
    order_items = []

    for item_data in items:
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item_data['product_id']} not found")
        if product.stock < item_data["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")

        line_total = round(product.price * item_data["quantity"], 2)
        total += line_total
        order_items.append({"product": product, "quantity": item_data["quantity"], "price": product.price})

    order = Order(user_id=user_id, total_amount=round(total, 2))
    db.add(order)
    db.flush()

    for oi in order_items:
        db.add(OrderItem(order_id=order.id, product_id=oi["product"].id, quantity=oi["quantity"], price=oi["price"]))
        oi["product"].stock -= oi["quantity"]
        oi["product"].sales_count += oi["quantity"]

    db.commit()
    db.refresh(order)
    return order


def get_user_orders(db: Session, user_id: int) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()


def get_order(db: Session, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()
```

- [ ] **Step 3: Create order router**

Create `backend/app/api/orders.py`:
```python
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
    items = [item.model_dump() for item in data.items]
    return create_order(db, user.id, items)


@router.get("", response_model=list[OrderResponse])
def list_mine(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_user_orders(db, user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_by_id(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = get_order(db, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
```

- [ ] **Step 4: Register router, run tests, commit**

Add `from app.api import auth, products, orders` and `app.include_router(orders.router)` to `main.py`.

```bash
cd backend && python -m pytest tests/test_api/test_orders.py -v
```

Expected: 3 tests PASS

```bash
git add backend/
git commit -m "feat: order creation with stock validation and order listing"
```

---

### Task 7: Community API (Reviews + QA)

**Files:**
- Create: `backend/app/services/community_service.py`
- Create: `backend/app/api/community.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_api/test_community.py`

- [ ] **Step 1: Write failing community tests**

Create `backend/tests/test_api/test_community.py`:
```python
import pytest
from app.models import User, Category, Product, UserRole


@pytest.fixture
def auth_header(client):
    client.post("/api/auth/register", json={
        "username": "reviewer", "email": "r@test.com", "password": "secret123"
    })
    resp = client.post("/api/auth/login", json={"username": "reviewer", "password": "secret123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def product_id(db):
    user = User(username="seller2", email="s2@t.com", hashed_password="h", role=UserRole.merchant)
    cat = Category(name="Food")
    db.add_all([user, cat])
    db.commit()
    p = Product(name="Snack", price=5.99, category_id=cat.id, merchant_id=user.id, stock=100)
    db.add(p)
    db.commit()
    return p.id


def test_create_review(client, auth_header, product_id):
    response = client.post("/api/reviews", json={
        "product_id": product_id, "rating": 5, "content": "Great!"
    }, headers=auth_header)
    assert response.status_code == 201
    assert response.json()["rating"] == 5


def test_get_product_reviews(client, auth_header, product_id):
    client.post("/api/reviews", json={
        "product_id": product_id, "rating": 4, "content": "Good"
    }, headers=auth_header)
    response = client.get(f"/api/reviews/product/{product_id}")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_helpful_review(client, auth_header, product_id):
    resp = client.post("/api/reviews", json={
        "product_id": product_id, "rating": 5, "content": "Awesome"
    }, headers=auth_header)
    review_id = resp.json()["id"]
    response = client.post(f"/api/reviews/{review_id}/helpful", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["helpful_count"] == 1


def test_create_qa(client, auth_header, product_id):
    response = client.post("/api/qa", json={
        "product_id": product_id, "question": "Is this organic?"
    }, headers=auth_header)
    assert response.status_code == 201
    assert response.json()["question"] == "Is this organic?"


def test_answer_qa(client, auth_header, product_id):
    resp = client.post("/api/qa", json={
        "product_id": product_id, "question": "Is this organic?"
    }, headers=auth_header)
    qa_id = resp.json()["id"]
    response = client.post(f"/api/qa/{qa_id}/answer", json={
        "answer": "Yes, 100% organic."
    }, headers=auth_header)
    assert response.status_code == 200
    assert response.json()["answer"] == "Yes, 100% organic."
```

- [ ] **Step 2: Create community service**

Create `backend/app/services/community_service.py`:
```python
from sqlalchemy.orm import Session

from app.models.community import QA, Review


def create_review(db: Session, user_id: int, product_id: int, rating: int, content: str) -> Review:
    review = Review(user_id=user_id, product_id=product_id, rating=rating, content=content)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_product_reviews(db: Session, product_id: int) -> list[Review]:
    return db.query(Review).filter(Review.product_id == product_id).order_by(Review.created_at.desc()).all()


def mark_helpful(db: Session, review_id: int) -> Review | None:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return None
    review.helpful_count += 1
    db.commit()
    db.refresh(review)
    return review


def create_question(db: Session, user_id: int, product_id: int, question: str) -> QA:
    qa = QA(user_id=user_id, product_id=product_id, question=question)
    db.add(qa)
    db.commit()
    db.refresh(qa)
    return qa


def answer_question(db: Session, qa_id: int, user_id: int, answer: str) -> QA | None:
    qa = db.query(QA).filter(QA.id == qa_id).first()
    if not qa:
        return None
    qa.answer = answer
    qa.answered_by = user_id
    db.commit()
    db.refresh(qa)
    return qa


def get_product_qa(db: Session, product_id: int) -> list[QA]:
    return db.query(QA).filter(QA.product_id == product_id).order_by(QA.created_at.desc()).all()
```

- [ ] **Step 3: Create community router**

Create `backend/app/api/community.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.community import QAAnswerCreate, QACreate, QAResponse, ReviewCreate, ReviewResponse
from app.services.community_service import (
    answer_question, create_question, create_review, get_product_qa, get_product_reviews, mark_helpful,
)

router = APIRouter(tags=["community"])


@router.post("/api/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def post_review(data: ReviewCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return create_review(db, user.id, data.product_id, data.rating, data.content)


@router.get("/api/reviews/product/{product_id}", response_model=list[ReviewResponse])
def list_reviews(product_id: int, db: Session = Depends(get_db)):
    return get_product_reviews(db, product_id)


@router.post("/api/reviews/{review_id}/helpful", response_model=ReviewResponse)
def helpful(review_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    review = mark_helpful(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/api/qa", response_model=QAResponse, status_code=status.HTTP_201_CREATED)
def post_question(data: QACreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return create_question(db, user.id, data.product_id, data.question)


@router.get("/api/qa/product/{product_id}", response_model=list[QAResponse])
def list_qa(product_id: int, db: Session = Depends(get_db)):
    return get_product_qa(db, product_id)


@router.post("/api/qa/{qa_id}/answer", response_model=QAResponse)
def post_answer(qa_id: int, data: QAAnswerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    qa = answer_question(db, qa_id, user.id, data.answer)
    if not qa:
        raise HTTPException(status_code=404, detail="Question not found")
    return qa
```

- [ ] **Step 4: Register router, run tests, commit**

Add `community` to main.py imports and `app.include_router(community.router)`.

```bash
cd backend && python -m pytest tests/test_api/test_community.py -v
```

Expected: 5 tests PASS

```bash
git add backend/
git commit -m "feat: community API with reviews, ratings, QA"
```

---

### Task 8: Behavior Tracking API

**Files:**
- Create: `backend/app/api/behavior.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_api/test_behavior.py`

- [ ] **Step 1: Write failing behavior test**

Create `backend/tests/test_api/test_behavior.py`:
```python
import pytest
from app.models import User, Category, Product, UserRole


@pytest.fixture
def auth_header(client):
    client.post("/api/auth/register", json={
        "username": "tracker", "email": "t@test.com", "password": "secret123"
    })
    resp = client.post("/api/auth/login", json={"username": "tracker", "password": "secret123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def product_id(db):
    user = User(username="s", email="s@t.com", hashed_password="h", role=UserRole.merchant)
    cat = Category(name="C")
    db.add_all([user, cat])
    db.commit()
    p = Product(name="Item", price=10.0, category_id=cat.id, merchant_id=user.id, stock=5)
    db.add(p)
    db.commit()
    return p.id


def test_track_view(client, auth_header, product_id):
    response = client.post("/api/behavior/track", json={
        "product_id": product_id, "behavior_type": "view",
        "context": {"source": "home"}
    }, headers=auth_header)
    assert response.status_code == 201


def test_track_search(client, auth_header):
    response = client.post("/api/behavior/track", json={
        "behavior_type": "search",
        "context": {"query": "laptop"}
    }, headers=auth_header)
    assert response.status_code == 201
```

- [ ] **Step 2: Create behavior router**

Create `backend/app/api/behavior.py`:
```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.behavior import BehaviorType, UserBehavior
from app.models.user import User
from app.schemas.community import BehaviorTrack

router = APIRouter(prefix="/api/behavior", tags=["behavior"])


@router.post("/track", status_code=status.HTTP_201_CREATED)
def track(data: BehaviorTrack, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    behavior = UserBehavior(
        user_id=user.id,
        product_id=data.product_id,
        behavior_type=BehaviorType(data.behavior_type),
        context=data.context,
    )
    db.add(behavior)
    db.commit()
    return {"status": "tracked"}
```

- [ ] **Step 3: Register router, run tests, commit**

Add `behavior` to main.py and register router.

```bash
cd backend && python -m pytest tests/test_api/test_behavior.py -v
```

Expected: 2 tests PASS

```bash
git add backend/
git commit -m "feat: user behavior tracking API"
```

---

## Phase 3: Activity Engine + Frequency Control

### Task 9: Activity Scorer

**Files:**
- Create: `backend/app/activity/scorer.py`
- Test: `backend/tests/test_activity/test_scorer.py`

- [ ] **Step 1: Write failing scorer tests**

Create `backend/tests/test_activity/test_scorer.py`:
```python
import math
from datetime import datetime, timedelta, timezone

from app.activity.scorer import (
    BEHAVIOR_WEIGHTS, calculate_activity_score, classify_activity_level, time_decay,
)


def test_time_decay_today():
    assert time_decay(0) == 1.0


def test_time_decay_7_days():
    result = time_decay(7)
    assert abs(result - math.exp(-0.7)) < 0.001


def test_time_decay_30_days():
    result = time_decay(30)
    assert result < 0.1


def test_behavior_weights_exist():
    assert BEHAVIOR_WEIGHTS["login"] == 2
    assert BEHAVIOR_WEIGHTS["purchase"] == 10
    assert BEHAVIOR_WEIGHTS["review"] == 5


def test_calculate_score_empty():
    assert calculate_activity_score([]) == 0.0


def test_calculate_score_single_login_today():
    now = datetime.now(timezone.utc)
    behaviors = [{"behavior_type": "login", "created_at": now}]
    score = calculate_activity_score(behaviors)
    assert abs(score - 2.0) < 0.01


def test_calculate_score_capped_at_100():
    now = datetime.now(timezone.utc)
    behaviors = [{"behavior_type": "purchase", "created_at": now}] * 20
    score = calculate_activity_score(behaviors)
    assert score == 100.0


def test_classify_high():
    assert classify_activity_level(60.0) == "high"
    assert classify_activity_level(100.0) == "high"


def test_classify_normal():
    assert classify_activity_level(20.0) == "normal"
    assert classify_activity_level(59.9) == "normal"


def test_classify_low():
    assert classify_activity_level(0.0) == "low"
    assert classify_activity_level(19.9) == "low"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && python -m pytest tests/test_activity/test_scorer.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement scorer**

Create `backend/app/activity/scorer.py`:
```python
import math
from datetime import datetime, timezone

BEHAVIOR_WEIGHTS = {
    "login": 2,
    "view": 1,
    "search": 1,
    "cart": 3,
    "purchase": 10,
    "review": 5,
    "answer": 5,
    "helpful": 2,
}

DECAY_LAMBDA = 0.1


def time_decay(days_ago: float) -> float:
    return math.exp(-DECAY_LAMBDA * days_ago)


def calculate_activity_score(behaviors: list[dict]) -> float:
    now = datetime.now(timezone.utc)
    score = 0.0
    for b in behaviors:
        weight = BEHAVIOR_WEIGHTS.get(b["behavior_type"], 0)
        created = b["created_at"]
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        days_ago = (now - created).total_seconds() / 86400
        score += weight * time_decay(max(0, days_ago))
    return min(100.0, round(score, 2))


def classify_activity_level(score: float) -> str:
    if score >= 60:
        return "high"
    elif score >= 20:
        return "normal"
    return "low"
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_activity/test_scorer.py -v
```

Expected: 10 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/activity/ backend/tests/test_activity/
git commit -m "feat: activity scoring engine with time-decay and level classification"
```

---

### Task 10: Frequency Control Component

**Files:**
- Create: `backend/app/ad_engine/frequency.py`
- Test: `backend/tests/test_ad_engine/test_frequency.py`

- [ ] **Step 1: Write failing frequency tests**

Create `backend/tests/test_ad_engine/test_frequency.py`:
```python
import time

from app.ad_engine.frequency import FrequencyController, FrequencyPolicy, get_policy


def test_get_policy_high():
    policy = get_policy("high")
    assert policy.ads_per_page == 3
    assert policy.daily_cap == 50
    assert policy.min_interval_sec == 60


def test_get_policy_normal():
    policy = get_policy("normal")
    assert policy.ads_per_page == 2
    assert policy.daily_cap == 30


def test_get_policy_low():
    policy = get_policy("low")
    assert policy.ads_per_page == 1
    assert policy.daily_cap == 10
    assert policy.min_interval_sec == 300


def test_controller_allows_first_request():
    ctrl = FrequencyController()
    result = ctrl.check(user_id=1, activity_level="normal", today_count=0, last_shown_ts=0)
    assert result["allowed"] is True
    assert result["max_ads"] == 2


def test_controller_blocks_daily_cap():
    ctrl = FrequencyController()
    result = ctrl.check(user_id=1, activity_level="low", today_count=10, last_shown_ts=0)
    assert result["allowed"] is False
    assert result["reason"] == "daily_cap_reached"


def test_controller_blocks_interval():
    ctrl = FrequencyController()
    now = time.time()
    result = ctrl.check(user_id=1, activity_level="normal", today_count=5, last_shown_ts=now - 10)
    assert result["allowed"] is False
    assert result["reason"] == "min_interval_not_met"


def test_controller_allows_after_interval():
    ctrl = FrequencyController()
    now = time.time()
    result = ctrl.check(user_id=1, activity_level="normal", today_count=5, last_shown_ts=now - 200)
    assert result["allowed"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && python -m pytest tests/test_ad_engine/test_frequency.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement frequency controller**

Create `backend/app/ad_engine/frequency.py`:
```python
import time
from dataclasses import dataclass


@dataclass
class FrequencyPolicy:
    ads_per_page: int
    min_interval_sec: int
    daily_cap: int


POLICIES = {
    "high": FrequencyPolicy(ads_per_page=3, min_interval_sec=60, daily_cap=50),
    "normal": FrequencyPolicy(ads_per_page=2, min_interval_sec=120, daily_cap=30),
    "low": FrequencyPolicy(ads_per_page=1, min_interval_sec=300, daily_cap=10),
}


def get_policy(activity_level: str) -> FrequencyPolicy:
    return POLICIES.get(activity_level, POLICIES["normal"])


class FrequencyController:
    def check(
        self, user_id: int, activity_level: str, today_count: int, last_shown_ts: float
    ) -> dict:
        policy = get_policy(activity_level)

        if today_count >= policy.daily_cap:
            return {"allowed": False, "reason": "daily_cap_reached", "max_ads": 0}

        now = time.time()
        if last_shown_ts > 0 and (now - last_shown_ts) < policy.min_interval_sec:
            return {"allowed": False, "reason": "min_interval_not_met", "max_ads": 0}

        remaining = policy.daily_cap - today_count
        max_ads = min(policy.ads_per_page, remaining)
        return {"allowed": True, "reason": "ok", "max_ads": max_ads}
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_ad_engine/test_frequency.py -v
```

Expected: 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/ad_engine/ backend/tests/test_ad_engine/
git commit -m "feat: frequency control component with activity-based ad limiting"
```

---

### Task 11: Ad Bidding and Billing

**Files:**
- Create: `backend/app/ad_engine/bidding.py`
- Create: `backend/app/ad_engine/billing.py`
- Test: `backend/tests/test_ad_engine/test_bidding.py`

- [ ] **Step 1: Write failing bidding/billing tests**

Create `backend/tests/test_ad_engine/test_bidding.py`:
```python
from app.ad_engine.bidding import rank_ads_by_ecpm
from app.ad_engine.billing import calculate_cpc_charge, calculate_cpm_charge


def test_rank_ads_by_ecpm():
    ads = [
        {"id": 1, "bid_amount": 1.0, "bid_type": "CPC", "pctr": 0.05},
        {"id": 2, "bid_amount": 0.5, "bid_type": "CPC", "pctr": 0.20},
        {"id": 3, "bid_amount": 2.0, "bid_type": "CPM", "pctr": 0.01},
    ]
    ranked = rank_ads_by_ecpm(ads)
    assert ranked[0]["id"] == 2  # 0.5 * 0.20 * 1000 = 100 eCPM
    assert ranked[1]["id"] == 1  # 1.0 * 0.05 * 1000 = 50 eCPM
    assert ranked[2]["id"] == 3  # 2.0 eCPM (CPM as-is)


def test_rank_empty():
    assert rank_ads_by_ecpm([]) == []


def test_cpc_charge():
    charge = calculate_cpc_charge(
        current_pctr=0.05,
        next_ecpm=40.0,  # next ad's eCPM
    )
    # charge = next_ecpm / current_pctr / 1000 + 0.01
    # = 40.0 / 0.05 / 1000 + 0.01 = 0.8 + 0.01 = 0.81
    assert abs(charge - 0.81) < 0.001


def test_cpm_charge():
    charge = calculate_cpm_charge(bid_amount=5.0)
    # CPM: charge per impression = bid / 1000
    assert abs(charge - 0.005) < 0.0001
```

- [ ] **Step 2: Implement bidding**

Create `backend/app/ad_engine/bidding.py`:
```python
def compute_ecpm(ad: dict) -> float:
    if ad["bid_type"] == "CPM":
        return ad["bid_amount"]
    return ad["bid_amount"] * ad.get("pctr", 0.01) * 1000


def rank_ads_by_ecpm(ads: list[dict]) -> list[dict]:
    for ad in ads:
        ad["ecpm"] = compute_ecpm(ad)
    return sorted(ads, key=lambda a: a["ecpm"], reverse=True)
```

- [ ] **Step 3: Implement billing**

Create `backend/app/ad_engine/billing.py`:
```python
def calculate_cpc_charge(current_pctr: float, next_ecpm: float) -> float:
    if current_pctr <= 0:
        return 0.01
    charge = next_ecpm / current_pctr / 1000 + 0.01
    return round(charge, 4)


def calculate_cpm_charge(bid_amount: float) -> float:
    return round(bid_amount / 1000, 4)
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_ad_engine/test_bidding.py -v
```

Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/ad_engine/ backend/tests/test_ad_engine/
git commit -m "feat: ad bidding (eCPM ranking) and billing (CPC/CPM)"
```

---

### Task 12: Ad API with Frequency Control Integration

**Files:**
- Create: `backend/app/services/ad_service.py`
- Create: `backend/app/api/ads.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_api/test_ads.py`

- [ ] **Step 1: Write failing ad API tests**

Create `backend/tests/test_api/test_ads.py`:
```python
import pytest
from app.models import User, UserRole


@pytest.fixture
def merchant_header(client):
    client.post("/api/auth/register", json={
        "username": "advertiser", "email": "adv@test.com", "password": "secret123"
    })
    from app.database import get_db
    db = next(client.app.dependency_overrides[get_db]())
    user = db.query(User).filter(User.username == "advertiser").first()
    user.role = UserRole.merchant
    db.commit()
    resp = client.post("/api/auth/login", json={"username": "advertiser", "password": "secret123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def consumer_header(client):
    client.post("/api/auth/register", json={
        "username": "consumer", "email": "c@test.com", "password": "secret123"
    })
    resp = client.post("/api/auth/login", json={"username": "consumer", "password": "secret123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_create_ad(client, merchant_header):
    response = client.post("/api/ads", json={
        "title": "Buy Now!", "bid_amount": 1.0,
        "daily_budget": 100.0, "total_budget": 1000.0,
        "target_tags": ["electronics"]
    }, headers=merchant_header)
    assert response.status_code == 201
    assert response.json()["title"] == "Buy Now!"


def test_fetch_ads(client, merchant_header, consumer_header):
    client.post("/api/ads", json={
        "title": "Sale!", "bid_amount": 2.0,
        "daily_budget": 100.0, "total_budget": 1000.0,
    }, headers=merchant_header)
    response = client.get("/api/ads/fetch", headers=consumer_header)
    assert response.status_code == 200
    data = response.json()
    assert "ads" in data
    assert "frequency_level" in data


def test_record_impression(client, merchant_header, consumer_header):
    resp = client.post("/api/ads", json={
        "title": "Click Me", "bid_amount": 1.5,
        "daily_budget": 100.0, "total_budget": 1000.0,
    }, headers=merchant_header)
    ad_id = resp.json()["id"]
    response = client.post("/api/ads/impression", json={
        "ad_id": ad_id, "impression_type": "click"
    }, headers=consumer_header)
    assert response.status_code == 201
```

- [ ] **Step 2: Create ad service**

Create `backend/app/services/ad_service.py`:
```python
import time
from datetime import date

from sqlalchemy.orm import Session

from app.activity.scorer import calculate_activity_score, classify_activity_level
from app.ad_engine.bidding import rank_ads_by_ecpm
from app.ad_engine.billing import calculate_cpc_charge, calculate_cpm_charge
from app.ad_engine.frequency import FrequencyController
from app.models.ad import Ad, AdImpression, AdStatus, ImpressionType
from app.models.behavior import UserBehavior
from app.models.user import AdFrequencyLevel, User

freq_controller = FrequencyController()


def create_ad(db: Session, advertiser_id: int, **kwargs) -> Ad:
    ad = Ad(advertiser_id=advertiser_id, **kwargs)
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


def fetch_ads_for_user(db: Session, user: User) -> dict:
    behaviors = db.query(UserBehavior).filter(UserBehavior.user_id == user.id).all()
    behavior_dicts = [{"behavior_type": b.behavior_type.value, "created_at": b.created_at} for b in behaviors]
    score = calculate_activity_score(behavior_dicts)
    level = classify_activity_level(score)

    today = date.today().isoformat()
    today_count = db.query(AdImpression).filter(
        AdImpression.user_id == user.id,
        AdImpression.impression_type == ImpressionType.show,
    ).count()

    last_impression = db.query(AdImpression).filter(
        AdImpression.user_id == user.id,
        AdImpression.impression_type == ImpressionType.show,
    ).order_by(AdImpression.created_at.desc()).first()
    last_ts = last_impression.created_at.timestamp() if last_impression else 0

    freq_result = freq_controller.check(user.id, level, today_count, last_ts)
    if not freq_result["allowed"]:
        return {"ads": [], "frequency_level": level, "remaining_today": 0}

    active_ads = db.query(Ad).filter(Ad.status == AdStatus.active).all()
    ad_dicts = [
        {"id": a.id, "bid_amount": a.bid_amount, "bid_type": a.bid_type.value, "pctr": 0.05, "ad": a}
        for a in active_ads
    ]
    ranked = rank_ads_by_ecpm(ad_dicts)
    selected = [r["ad"] for r in ranked[: freq_result["max_ads"]]]

    remaining = freq_result["max_ads"]
    return {"ads": selected, "frequency_level": level, "remaining_today": remaining}


def record_impression(db: Session, user_id: int, ad_id: int, impression_type: str, context: dict | None) -> None:
    imp = AdImpression(
        ad_id=ad_id, user_id=user_id,
        impression_type=ImpressionType(impression_type),
        context=context,
    )
    db.add(imp)

    if impression_type == "click":
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if ad and ad.bid_type.value == "CPC":
            charge = calculate_cpc_charge(0.05, 0.0)
            ad.spent_amount += charge
            if ad.spent_amount >= ad.total_budget:
                ad.status = AdStatus.exhausted

    db.commit()


def get_merchant_ads(db: Session, advertiser_id: int) -> list[Ad]:
    return db.query(Ad).filter(Ad.advertiser_id == advertiser_id).all()


def get_ad_stats(db: Session, ad_id: int) -> dict:
    shows = db.query(AdImpression).filter(AdImpression.ad_id == ad_id, AdImpression.impression_type == ImpressionType.show).count()
    clicks = db.query(AdImpression).filter(AdImpression.ad_id == ad_id, AdImpression.impression_type == ImpressionType.click).count()
    converts = db.query(AdImpression).filter(AdImpression.ad_id == ad_id, AdImpression.impression_type == ImpressionType.convert).count()
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    ctr = clicks / shows if shows > 0 else 0.0
    return {
        "ad_id": ad_id, "total_shows": shows, "total_clicks": clicks,
        "total_converts": converts, "ctr": round(ctr, 4),
        "spent": ad.spent_amount if ad else 0.0,
    }
```

- [ ] **Step 3: Create ad router**

Create `backend/app/api/ads.py`:
```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_merchant
from app.database import get_db
from app.models.user import User
from app.schemas.ad import AdCreate, AdFetchResponse, AdResponse, AdStatsResponse, ImpressionCreate
from app.services.ad_service import create_ad, fetch_ads_for_user, get_ad_stats, get_merchant_ads, record_impression

router = APIRouter(prefix="/api/ads", tags=["ads"])


@router.post("", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
def create(data: AdCreate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    return create_ad(db, user.id, **data.model_dump())


@router.get("/fetch", response_model=AdFetchResponse)
def fetch(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return fetch_ads_for_user(db, user)


@router.post("/impression", status_code=status.HTTP_201_CREATED)
def impression(data: ImpressionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record_impression(db, user.id, data.ad_id, data.impression_type.value, data.context)
    return {"status": "recorded"}


@router.get("/my", response_model=list[AdResponse])
def my_ads(db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    return get_merchant_ads(db, user.id)


@router.get("/{ad_id}/stats", response_model=AdStatsResponse)
def stats(ad_id: int, db: Session = Depends(get_db), _user: User = Depends(require_merchant)):
    return get_ad_stats(db, ad_id)
```

- [ ] **Step 4: Register router, run tests, commit**

Add `ads` to main.py imports and register.

```bash
cd backend && python -m pytest tests/test_api/test_ads.py -v
```

Expected: 3 tests PASS

```bash
git add backend/
git commit -m "feat: ad API with bidding, billing, and frequency control integration"
```

---

### Task 13: Activity API

**Files:**
- Create: `backend/app/api/activity.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_api/test_activity.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_api/test_activity.py`:
```python
def test_my_activity_score(client):
    client.post("/api/auth/register", json={
        "username": "active_user", "email": "a@test.com", "password": "secret123"
    })
    resp = client.post("/api/auth/login", json={"username": "active_user", "password": "secret123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/activity/my-score", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "level" in data
    assert data["level"] in ("low", "normal", "high")
```

- [ ] **Step 2: Create activity router**

Create `backend/app/api/activity.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.activity.scorer import calculate_activity_score, classify_activity_level
from app.api.deps import get_current_user
from app.database import get_db
from app.models.behavior import UserBehavior
from app.models.user import User
from app.schemas.community import ActivityScoreResponse

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("/my-score", response_model=ActivityScoreResponse)
def my_score(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    behaviors = db.query(UserBehavior).filter(UserBehavior.user_id == user.id).all()
    behavior_dicts = [{"behavior_type": b.behavior_type.value, "created_at": b.created_at} for b in behaviors]
    score = calculate_activity_score(behavior_dicts)
    level = classify_activity_level(score)
    return ActivityScoreResponse(score=score, level=level, ad_frequency_level=level)
```

- [ ] **Step 3: Register router, run test, commit**

Add `activity` to main.py and register.

```bash
cd backend && python -m pytest tests/test_api/test_activity.py -v
```

Expected: PASS

```bash
git add backend/
git commit -m "feat: activity score API endpoint"
```

---

## Phase 4: Recommendation Engine

### Task 14: Recall Layer — UserCF and ItemCF

**Files:**
- Create: `backend/app/recommendation/recall/user_cf.py`
- Create: `backend/app/recommendation/recall/item_cf.py`
- Test: `backend/tests/test_recommendation/test_cf.py`

- [ ] **Step 1: Write failing CF tests**

Create `backend/tests/test_recommendation/test_cf.py`:
```python
import numpy as np

from app.recommendation.recall.user_cf import UserCF
from app.recommendation.recall.item_cf import ItemCF


def test_user_cf_fit_and_recommend():
    # Rows=users, Cols=products. Values=implicit rating.
    interaction_matrix = np.array([
        [5, 3, 0, 1],
        [4, 0, 0, 1],
        [1, 1, 0, 5],
        [0, 0, 5, 4],
    ], dtype=float)

    ucf = UserCF()
    ucf.fit(interaction_matrix)
    # User 1 (index 1) hasn't rated item 1 (index 1). User 0 is most similar and rated it 3.
    recs = ucf.recommend(user_idx=1, n=2, exclude_interacted=True)
    assert len(recs) <= 2
    assert all(isinstance(r, int) for r in recs)


def test_user_cf_empty_history():
    matrix = np.array([[0, 0, 0], [1, 0, 1]], dtype=float)
    ucf = UserCF()
    ucf.fit(matrix)
    recs = ucf.recommend(user_idx=0, n=2, exclude_interacted=True)
    assert isinstance(recs, list)


def test_item_cf_fit_and_recommend():
    interaction_matrix = np.array([
        [5, 3, 0, 1],
        [4, 0, 0, 1],
        [1, 1, 0, 5],
        [0, 0, 5, 4],
    ], dtype=float)

    icf = ItemCF()
    icf.fit(interaction_matrix)
    recs = icf.recommend(user_idx=0, n=2, exclude_interacted=True)
    assert len(recs) <= 2
    # Item 2 (index 2) is not interacted by user 0, should appear
    assert 2 in recs
```

- [ ] **Step 2: Implement UserCF**

Create `backend/app/recommendation/recall/user_cf.py`:
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class UserCF:
    def __init__(self):
        self.user_sim_matrix = None
        self.interaction_matrix = None

    def fit(self, interaction_matrix: np.ndarray):
        self.interaction_matrix = interaction_matrix
        self.user_sim_matrix = cosine_similarity(interaction_matrix)
        np.fill_diagonal(self.user_sim_matrix, 0)

    def recommend(self, user_idx: int, n: int = 10, exclude_interacted: bool = True) -> list[int]:
        if self.user_sim_matrix is None:
            return []

        sim_scores = self.user_sim_matrix[user_idx]
        weighted_scores = sim_scores @ self.interaction_matrix

        if exclude_interacted:
            interacted = self.interaction_matrix[user_idx] > 0
            weighted_scores[interacted] = -1

        top_indices = np.argsort(weighted_scores)[::-1][:n]
        return [int(i) for i in top_indices if weighted_scores[i] > 0]
```

- [ ] **Step 3: Implement ItemCF**

Create `backend/app/recommendation/recall/item_cf.py`:
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class ItemCF:
    def __init__(self):
        self.item_sim_matrix = None
        self.interaction_matrix = None

    def fit(self, interaction_matrix: np.ndarray):
        self.interaction_matrix = interaction_matrix
        self.item_sim_matrix = cosine_similarity(interaction_matrix.T)
        np.fill_diagonal(self.item_sim_matrix, 0)

    def recommend(self, user_idx: int, n: int = 10, exclude_interacted: bool = True) -> list[int]:
        if self.item_sim_matrix is None:
            return []

        user_ratings = self.interaction_matrix[user_idx]
        scores = user_ratings @ self.item_sim_matrix

        if exclude_interacted:
            interacted = user_ratings > 0
            scores[interacted] = -1

        top_indices = np.argsort(scores)[::-1][:n]
        return [int(i) for i in top_indices if scores[i] > 0]
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_recommendation/test_cf.py -v
```

Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/recommendation/ backend/tests/test_recommendation/
git commit -m "feat: UserCF and ItemCF collaborative filtering recall"
```

---

### Task 15: Recall Layer — Content-Based and ALS

**Files:**
- Create: `backend/app/recommendation/recall/content_based.py`
- Create: `backend/app/recommendation/recall/als.py`
- Create: `backend/app/recommendation/recall/hot.py`
- Test: `backend/tests/test_recommendation/test_recall.py`

- [ ] **Step 1: Write failing recall tests**

Create `backend/tests/test_recommendation/test_recall.py`:
```python
import numpy as np

from app.recommendation.recall.content_based import ContentBasedRecall
from app.recommendation.recall.als import ALSRecall
from app.recommendation.recall.hot import HotRecall


def test_content_based():
    product_tags = [
        "laptop computer gaming",
        "phone mobile smartphone",
        "laptop ultrabook portable",
        "headphones audio music",
    ]
    cb = ContentBasedRecall()
    cb.fit(product_tags)
    # User likes laptops (indices 0, 2). Recommend similar.
    recs = cb.recommend(liked_indices=[0], n=2, exclude_indices=[0])
    assert 2 in recs  # ultrabook laptop is most similar


def test_content_based_empty():
    cb = ContentBasedRecall()
    cb.fit(["a", "b"])
    recs = cb.recommend(liked_indices=[], n=2)
    assert recs == []


def test_als_recall():
    matrix = np.array([
        [5, 3, 0, 1],
        [4, 0, 0, 1],
        [1, 1, 0, 5],
        [0, 0, 5, 4],
    ], dtype=float)
    als = ALSRecall(n_components=2)
    als.fit(matrix)
    recs = als.recommend(user_idx=1, n=2, exclude_interacted=True)
    assert len(recs) <= 2


def test_hot_recall():
    hot = HotRecall()
    hot.update({10: 500, 20: 300, 30: 100, 40: 800})
    recs = hot.recommend(n=2)
    assert recs[0] == 40  # highest views
    assert recs[1] == 10
```

- [ ] **Step 2: Implement ContentBasedRecall**

Create `backend/app/recommendation/recall/content_based.py`:
```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecall:
    def __init__(self):
        self.tfidf_matrix = None
        self.sim_matrix = None

    def fit(self, product_texts: list[str]):
        vectorizer = TfidfVectorizer()
        self.tfidf_matrix = vectorizer.fit_transform(product_texts)
        self.sim_matrix = cosine_similarity(self.tfidf_matrix)
        np.fill_diagonal(self.sim_matrix, 0)

    def recommend(self, liked_indices: list[int], n: int = 10, exclude_indices: list[int] | None = None) -> list[int]:
        if self.sim_matrix is None or not liked_indices:
            return []

        scores = np.mean(self.sim_matrix[liked_indices], axis=0)
        if exclude_indices:
            for idx in exclude_indices:
                scores[idx] = -1

        top_indices = np.argsort(scores)[::-1][:n]
        return [int(i) for i in top_indices if scores[i] > 0]
```

- [ ] **Step 3: Implement ALSRecall**

Create `backend/app/recommendation/recall/als.py`:
```python
import numpy as np
from sklearn.decomposition import NMF


class ALSRecall:
    def __init__(self, n_components: int = 10):
        self.n_components = n_components
        self.user_factors = None
        self.item_factors = None
        self.interaction_matrix = None

    def fit(self, interaction_matrix: np.ndarray):
        self.interaction_matrix = interaction_matrix
        n_components = min(self.n_components, min(interaction_matrix.shape))
        model = NMF(n_components=n_components, init="random", random_state=42, max_iter=200)
        self.user_factors = model.fit_transform(interaction_matrix)
        self.item_factors = model.components_.T

    def recommend(self, user_idx: int, n: int = 10, exclude_interacted: bool = True) -> list[int]:
        if self.user_factors is None:
            return []

        scores = self.user_factors[user_idx] @ self.item_factors.T

        if exclude_interacted:
            interacted = self.interaction_matrix[user_idx] > 0
            scores[interacted] = -1

        top_indices = np.argsort(scores)[::-1][:n]
        return [int(i) for i in top_indices if scores[i] > 0]
```

- [ ] **Step 4: Implement HotRecall**

Create `backend/app/recommendation/recall/hot.py`:
```python
class HotRecall:
    def __init__(self):
        self.product_scores: dict[int, float] = {}

    def update(self, scores: dict[int, float]):
        self.product_scores = scores

    def recommend(self, n: int = 10, exclude_ids: set[int] | None = None) -> list[int]:
        exclude = exclude_ids or set()
        sorted_items = sorted(
            ((pid, score) for pid, score in self.product_scores.items() if pid not in exclude),
            key=lambda x: x[1],
            reverse=True,
        )
        return [pid for pid, _ in sorted_items[:n]]
```

- [ ] **Step 5: Run tests**

```bash
cd backend && python -m pytest tests/test_recommendation/test_recall.py -v
```

Expected: 4 tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/recommendation/ backend/tests/test_recommendation/
git commit -m "feat: content-based, ALS, and hot recall algorithms"
```

---

### Task 16: Ranking Layer — DeepFM

**Files:**
- Create: `backend/app/recommendation/ranking/features.py`
- Create: `backend/app/recommendation/ranking/deepfm.py`
- Test: `backend/tests/test_recommendation/test_deepfm.py`

- [ ] **Step 1: Write failing DeepFM tests**

Create `backend/tests/test_recommendation/test_deepfm.py`:
```python
import torch
import numpy as np

from app.recommendation.ranking.deepfm import DeepFM
from app.recommendation.ranking.features import FeatureEncoder


def test_feature_encoder():
    encoder = FeatureEncoder(
        sparse_dims={"user_id": 100, "product_id": 200, "category_id": 20},
        dense_count=5,
    )
    sparse = {"user_id": 1, "product_id": 50, "category_id": 3}
    dense = [0.5, 0.3, 10.0, 0.8, 1.0]
    result = encoder.encode(sparse, dense)
    assert "sparse_indices" in result
    assert "dense_values" in result
    assert len(result["sparse_indices"]) == 3
    assert len(result["dense_values"]) == 5


def test_deepfm_forward():
    model = DeepFM(
        sparse_field_dims=[100, 200, 20],
        embed_dim=8,
        dense_dim=5,
        hidden_dims=[64, 32],
    )
    batch_size = 4
    sparse_input = torch.tensor([[1, 50, 3], [2, 60, 5], [3, 70, 1], [4, 80, 2]])
    dense_input = torch.randn(batch_size, 5)
    output = model(sparse_input, dense_input)
    assert output.shape == (batch_size, 1)
    assert (output >= 0).all() and (output <= 1).all()


def test_deepfm_backward():
    model = DeepFM(sparse_field_dims=[10, 20], embed_dim=4, dense_dim=2, hidden_dims=[16])
    sparse = torch.tensor([[1, 5], [2, 10]])
    dense = torch.randn(2, 2)
    labels = torch.tensor([[1.0], [0.0]])

    output = model(sparse, dense)
    loss = torch.nn.BCELoss()(output, labels)
    loss.backward()

    has_grad = any(p.grad is not None for p in model.parameters())
    assert has_grad
```

- [ ] **Step 2: Implement FeatureEncoder**

Create `backend/app/recommendation/ranking/features.py`:
```python
class FeatureEncoder:
    def __init__(self, sparse_dims: dict[str, int], dense_count: int):
        self.sparse_fields = list(sparse_dims.keys())
        self.sparse_dims = sparse_dims
        self.dense_count = dense_count

    def encode(self, sparse: dict[str, int], dense: list[float]) -> dict:
        sparse_indices = [sparse[field] for field in self.sparse_fields]
        return {
            "sparse_indices": sparse_indices,
            "dense_values": dense,
        }
```

- [ ] **Step 3: Implement DeepFM**

Create `backend/app/recommendation/ranking/deepfm.py`:
```python
import torch
import torch.nn as nn


class FMLayer(nn.Module):
    def __init__(self, embed_dim: int, num_fields: int):
        super().__init__()
        self.num_fields = num_fields

    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:
        # embeddings: (batch, num_fields, embed_dim)
        sum_square = embeddings.sum(dim=1).pow(2)
        square_sum = embeddings.pow(2).sum(dim=1)
        return 0.5 * (sum_square - square_sum).sum(dim=1, keepdim=True)


class DeepFM(nn.Module):
    def __init__(self, sparse_field_dims: list[int], embed_dim: int, dense_dim: int, hidden_dims: list[int]):
        super().__init__()
        self.embeddings = nn.ModuleList([
            nn.Embedding(dim, embed_dim) for dim in sparse_field_dims
        ])
        num_fields = len(sparse_field_dims)
        self.fm = FMLayer(embed_dim, num_fields)

        dnn_input_dim = num_fields * embed_dim + dense_dim
        layers = []
        in_dim = dnn_input_dim
        for h_dim in hidden_dims:
            layers.extend([nn.Linear(in_dim, h_dim), nn.ReLU(), nn.Dropout(0.2)])
            in_dim = h_dim
        layers.append(nn.Linear(in_dim, 1))
        self.dnn = nn.Sequential(*layers)
        self.output_layer = nn.Sigmoid()

    def forward(self, sparse_input: torch.Tensor, dense_input: torch.Tensor) -> torch.Tensor:
        # sparse_input: (batch, num_fields) — each value is an index
        embed_list = [self.embeddings[i](sparse_input[:, i]) for i in range(sparse_input.shape[1])]
        embed_stack = torch.stack(embed_list, dim=1)  # (batch, num_fields, embed_dim)

        fm_out = self.fm(embed_stack)  # (batch, 1)
        embed_flat = embed_stack.view(embed_stack.size(0), -1)  # (batch, num_fields * embed_dim)
        dnn_input = torch.cat([embed_flat, dense_input], dim=1)
        dnn_out = self.dnn(dnn_input)  # (batch, 1)

        return self.output_layer(fm_out + dnn_out)
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_recommendation/test_deepfm.py -v
```

Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/recommendation/ranking/ backend/tests/test_recommendation/
git commit -m "feat: DeepFM ranking model with feature encoder"
```

---

### Task 17: Ranking Layer — DIN (Deep Interest Network)

**Files:**
- Create: `backend/app/recommendation/ranking/din.py`
- Test: `backend/tests/test_recommendation/test_din.py`

- [ ] **Step 1: Write failing DIN tests**

Create `backend/tests/test_recommendation/test_din.py`:
```python
import torch

from app.recommendation.ranking.din import DIN


def test_din_forward():
    model = DIN(
        num_products=200,
        embed_dim=8,
        hidden_dims=[32, 16],
        max_seq_len=20,
    )
    batch_size = 4
    # behavior_seq: (batch, seq_len) — product IDs in user's history
    behavior_seq = torch.randint(0, 200, (batch_size, 20))
    # seq_lengths: actual length of each sequence
    seq_lengths = torch.tensor([10, 15, 5, 20])
    # candidate: (batch,) — candidate product ID
    candidate = torch.randint(0, 200, (batch_size,))

    output = model(behavior_seq, seq_lengths, candidate)
    assert output.shape == (batch_size, 1)
    assert (output >= 0).all() and (output <= 1).all()


def test_din_backward():
    model = DIN(num_products=50, embed_dim=4, hidden_dims=[16], max_seq_len=5)
    seq = torch.randint(0, 50, (2, 5))
    lengths = torch.tensor([3, 5])
    cand = torch.randint(0, 50, (2,))
    labels = torch.tensor([[1.0], [0.0]])

    out = model(seq, lengths, cand)
    loss = torch.nn.BCELoss()(out, labels)
    loss.backward()
    assert any(p.grad is not None for p in model.parameters())
```

- [ ] **Step 2: Implement DIN**

Create `backend/app/recommendation/ranking/din.py`:
```python
import torch
import torch.nn as nn


class AttentionLayer(nn.Module):
    def __init__(self, embed_dim: int):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(embed_dim * 4, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, queries: torch.Tensor, keys: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        # queries: (batch, 1, dim), keys: (batch, seq_len, dim)
        queries = queries.expand_as(keys)
        attn_input = torch.cat([queries, keys, queries - keys, queries * keys], dim=-1)
        attn_scores = self.attn(attn_input).squeeze(-1)  # (batch, seq_len)
        attn_scores = attn_scores.masked_fill(~mask, float("-inf"))
        attn_weights = torch.softmax(attn_scores, dim=-1)
        attn_weights = attn_weights.unsqueeze(1)  # (batch, 1, seq_len)
        return torch.bmm(attn_weights, keys).squeeze(1)  # (batch, dim)


class DIN(nn.Module):
    def __init__(self, num_products: int, embed_dim: int, hidden_dims: list[int], max_seq_len: int):
        super().__init__()
        self.product_embedding = nn.Embedding(num_products, embed_dim)
        self.attention = AttentionLayer(embed_dim)
        self.max_seq_len = max_seq_len

        dnn_input = embed_dim * 2
        layers = []
        in_dim = dnn_input
        for h in hidden_dims:
            layers.extend([nn.Linear(in_dim, h), nn.ReLU(), nn.Dropout(0.2)])
            in_dim = h
        layers.append(nn.Linear(in_dim, 1))
        self.dnn = nn.Sequential(*layers)
        self.output = nn.Sigmoid()

    def forward(self, behavior_seq: torch.Tensor, seq_lengths: torch.Tensor, candidate: torch.Tensor) -> torch.Tensor:
        seq_embed = self.product_embedding(behavior_seq)  # (batch, seq_len, dim)
        cand_embed = self.product_embedding(candidate).unsqueeze(1)  # (batch, 1, dim)

        mask = torch.arange(behavior_seq.size(1), device=behavior_seq.device).unsqueeze(0) < seq_lengths.unsqueeze(1)
        user_interest = self.attention(cand_embed, seq_embed, mask)  # (batch, dim)

        dnn_input = torch.cat([user_interest, cand_embed.squeeze(1)], dim=1)
        return self.output(self.dnn(dnn_input))
```

- [ ] **Step 3: Run tests**

```bash
cd backend && python -m pytest tests/test_recommendation/test_din.py -v
```

Expected: 2 tests PASS

- [ ] **Step 4: Commit**

```bash
git add backend/app/recommendation/ranking/ backend/tests/test_recommendation/
git commit -m "feat: DIN (Deep Interest Network) ranking model with attention"
```

---

### Task 18: Rerank Layer (Diversity + Rules)

**Files:**
- Create: `backend/app/recommendation/rerank/diversity.py`
- Create: `backend/app/recommendation/rerank/rules.py`
- Test: `backend/tests/test_recommendation/test_rerank.py`

- [ ] **Step 1: Write failing rerank tests**

Create `backend/tests/test_recommendation/test_rerank.py`:
```python
from app.recommendation.rerank.diversity import mmr_rerank
from app.recommendation.rerank.rules import apply_business_rules


def test_mmr_basic():
    items = [
        {"id": 1, "score": 0.9, "category": "A"},
        {"id": 2, "score": 0.85, "category": "A"},
        {"id": 3, "score": 0.8, "category": "B"},
        {"id": 4, "score": 0.7, "category": "C"},
    ]
    result = mmr_rerank(items, n=3, lambda_param=0.5)
    assert len(result) == 3
    categories = [r["category"] for r in result]
    assert len(set(categories)) >= 2  # Ensures diversity


def test_mmr_empty():
    assert mmr_rerank([], n=5) == []


def test_business_rules_filter_purchased():
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    purchased_ids = {2}
    result = apply_business_rules(items, purchased_ids=purchased_ids, shown_ids=set())
    assert len(result) == 2
    assert all(r["id"] != 2 for r in result)


def test_business_rules_filter_shown():
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    result = apply_business_rules(items, purchased_ids=set(), shown_ids={1, 3})
    assert len(result) == 1
    assert result[0]["id"] == 2
```

- [ ] **Step 2: Implement MMR diversity**

Create `backend/app/recommendation/rerank/diversity.py`:
```python
def mmr_rerank(items: list[dict], n: int = 10, lambda_param: float = 0.5) -> list[dict]:
    if not items:
        return []

    selected = [items[0]]
    remaining = items[1:]

    while len(selected) < n and remaining:
        best_score = -float("inf")
        best_idx = 0

        for i, item in enumerate(remaining):
            relevance = item.get("score", 0)
            max_sim = max(
                (1.0 if item.get("category") == s.get("category") else 0.0)
                for s in selected
            )
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i

        selected.append(remaining.pop(best_idx))

    return selected
```

- [ ] **Step 3: Implement business rules**

Create `backend/app/recommendation/rerank/rules.py`:
```python
def apply_business_rules(
    items: list[dict],
    purchased_ids: set[int],
    shown_ids: set[int],
) -> list[dict]:
    return [
        item for item in items
        if item["id"] not in purchased_ids and item["id"] not in shown_ids
    ]
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_recommendation/test_rerank.py -v
```

Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/recommendation/rerank/ backend/tests/test_recommendation/
git commit -m "feat: rerank layer with MMR diversity and business rules"
```

---

### Task 19: Recommendation Pipeline + API

**Files:**
- Create: `backend/app/recommendation/pipeline.py`
- Create: `backend/app/api/recommend.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_recommendation/test_pipeline.py`
- Test: `backend/tests/test_api/test_recommend.py`

- [ ] **Step 1: Write failing pipeline tests**

Create `backend/tests/test_recommendation/test_pipeline.py`:
```python
from app.recommendation.pipeline import RecommendationPipeline


def test_pipeline_cold_start():
    pipeline = RecommendationPipeline()
    # No data fitted — should return hot/fallback items
    result = pipeline.recommend(user_idx=None, n=5, product_ids=list(range(10)))
    assert isinstance(result, list)


def test_pipeline_returns_list():
    pipeline = RecommendationPipeline()
    result = pipeline.recommend(user_idx=None, n=3, product_ids=[1, 2, 3])
    assert isinstance(result, list)
    assert len(result) <= 3
```

- [ ] **Step 2: Implement pipeline**

Create `backend/app/recommendation/pipeline.py`:
```python
import random

import numpy as np

from app.recommendation.recall.content_based import ContentBasedRecall
from app.recommendation.recall.hot import HotRecall
from app.recommendation.recall.item_cf import ItemCF
from app.recommendation.recall.user_cf import UserCF
from app.recommendation.rerank.diversity import mmr_rerank
from app.recommendation.rerank.rules import apply_business_rules


class RecommendationPipeline:
    def __init__(self):
        self.user_cf = UserCF()
        self.item_cf = ItemCF()
        self.content_based = ContentBasedRecall()
        self.hot = HotRecall()
        self._fitted = False

    def fit(self, interaction_matrix: np.ndarray, product_texts: list[str], product_views: dict[int, float]):
        self.user_cf.fit(interaction_matrix)
        self.item_cf.fit(interaction_matrix)
        self.content_based.fit(product_texts)
        self.hot.update(product_views)
        self._fitted = True

    def recommend(
        self,
        user_idx: int | None,
        n: int = 10,
        product_ids: list[int] | None = None,
        purchased_ids: set[int] | None = None,
    ) -> list[int]:
        product_ids = product_ids or []
        purchased_ids = purchased_ids or set()

        if not self._fitted or user_idx is None:
            hot_recs = self.hot.recommend(n=n * 2, exclude_ids=purchased_ids)
            if hot_recs:
                return hot_recs[:n]
            candidates = [pid for pid in product_ids if pid not in purchased_ids]
            random.shuffle(candidates)
            return candidates[:n]

        candidates = set()
        for recall_fn in [
            lambda: self.user_cf.recommend(user_idx, n=n * 3),
            lambda: self.item_cf.recommend(user_idx, n=n * 3),
        ]:
            candidates.update(recall_fn())

        candidate_items = [
            {"id": pid, "score": 1.0 / (rank + 1), "category": "default"}
            for rank, pid in enumerate(candidates)
            if pid < len(product_ids)
        ]

        filtered = apply_business_rules(candidate_items, purchased_ids, set())
        reranked = mmr_rerank(filtered, n=n)
        result = [item["id"] for item in reranked]

        if len(result) < n:
            hot_fill = self.hot.recommend(n=n - len(result), exclude_ids=set(result) | purchased_ids)
            result.extend(hot_fill)

        return result[:n]
```

- [ ] **Step 3: Run pipeline tests**

```bash
cd backend && python -m pytest tests/test_recommendation/test_pipeline.py -v
```

Expected: 2 tests PASS

- [ ] **Step 4: Write API test**

Create `backend/tests/test_api/test_recommend.py`:
```python
import pytest
from app.models import User, Category, Product, UserRole


@pytest.fixture
def setup_products(db):
    user = User(username="m", email="m@t.com", hashed_password="h", role=UserRole.merchant)
    cat = Category(name="Electronics")
    db.add_all([user, cat])
    db.commit()
    for i in range(5):
        db.add(Product(name=f"Product {i}", price=10.0 + i, category_id=cat.id, merchant_id=user.id, stock=10))
    db.commit()


@pytest.fixture
def auth_header(client):
    client.post("/api/auth/register", json={
        "username": "user1", "email": "u1@t.com", "password": "s"
    })
    resp = client.post("/api/auth/login", json={"username": "user1", "password": "s"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_home_recommendations(client, auth_header, setup_products):
    response = client.get("/api/recommend/home", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_similar_products(client, auth_header, setup_products):
    response = client.get("/api/recommend/similar/1", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

- [ ] **Step 5: Create recommend router**

Create `backend/app/api/recommend.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


@router.get("/home", response_model=list[ProductResponse])
def home(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    products = db.query(Product).order_by(Product.sales_count.desc()).limit(20).all()
    return products


@router.get("/similar/{product_id}", response_model=list[ProductResponse])
def similar(product_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return []
    similar_products = db.query(Product).filter(
        Product.category_id == product.category_id,
        Product.id != product_id,
    ).limit(10).all()
    return similar_products


@router.get("/for-you", response_model=list[ProductResponse])
def for_you(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    products = db.query(Product).order_by(Product.created_at.desc()).limit(20).all()
    return products
```

- [ ] **Step 6: Register router, run tests, commit**

Add `recommend` to main.py and register.

```bash
cd backend && python -m pytest tests/test_api/test_recommend.py tests/test_recommendation/ -v
```

Expected: all PASS

```bash
git add backend/
git commit -m "feat: recommendation pipeline with multi-recall + rerank + API"
```

---

## Phase 5: Analytics + Seed Data

### Task 20: Analytics API

**Files:**
- Create: `backend/app/api/analytics.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_api/test_analytics.py`

- [ ] **Step 1: Write test**

Create `backend/tests/test_api/test_analytics.py`:
```python
import pytest
from app.models import User, UserRole


@pytest.fixture
def admin_header(client):
    client.post("/api/auth/register", json={
        "username": "admin", "email": "admin@test.com", "password": "secret123"
    })
    from app.database import get_db
    db = next(client.app.dependency_overrides[get_db]())
    user = db.query(User).filter(User.username == "admin").first()
    user.role = UserRole.admin
    db.commit()
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "secret123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_dashboard(client, admin_header):
    response = client.get("/api/analytics/dashboard", headers=admin_header)
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_products" in data
    assert "total_orders" in data
    assert "total_revenue" in data


def test_activity_distribution(client, admin_header):
    response = client.get("/api/analytics/activity-dist", headers=admin_header)
    assert response.status_code == 200
    data = response.json()
    assert "low" in data
    assert "normal" in data
    assert "high" in data
```

- [ ] **Step 2: Create analytics router**

Create `backend/app/api/analytics.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.database import get_db
from app.models.ad import Ad, AdImpression, ImpressionType
from app.models.order import Order
from app.models.product import Product
from app.models.user import AdFrequencyLevel, User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _user: User = Depends(require_admin)):
    total_users = db.query(func.count(User.id)).scalar()
    total_products = db.query(func.count(Product.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
    total_ad_revenue = db.query(func.sum(Ad.spent_amount)).scalar() or 0
    total_shows = db.query(func.count(AdImpression.id)).filter(AdImpression.impression_type == ImpressionType.show).scalar()
    total_clicks = db.query(func.count(AdImpression.id)).filter(AdImpression.impression_type == ImpressionType.click).scalar()
    ctr = total_clicks / total_shows if total_shows > 0 else 0
    rpm = total_ad_revenue / total_shows * 1000 if total_shows > 0 else 0
    return {
        "total_users": total_users, "total_products": total_products,
        "total_orders": total_orders, "total_revenue": round(total_revenue, 2),
        "total_ad_revenue": round(total_ad_revenue, 2),
        "ctr": round(ctr, 4), "rpm": round(rpm, 2),
    }


@router.get("/activity-dist")
def activity_dist(db: Session = Depends(get_db), _user: User = Depends(require_admin)):
    low = db.query(func.count(User.id)).filter(User.activity_score < 20).scalar()
    normal = db.query(func.count(User.id)).filter(User.activity_score >= 20, User.activity_score < 60).scalar()
    high = db.query(func.count(User.id)).filter(User.activity_score >= 60).scalar()
    return {"low": low, "normal": normal, "high": high}


@router.get("/ad-performance")
def ad_performance(db: Session = Depends(get_db), _user: User = Depends(require_admin)):
    ads = db.query(Ad).all()
    result = []
    for ad in ads:
        shows = db.query(func.count(AdImpression.id)).filter(
            AdImpression.ad_id == ad.id, AdImpression.impression_type == ImpressionType.show
        ).scalar()
        clicks = db.query(func.count(AdImpression.id)).filter(
            AdImpression.ad_id == ad.id, AdImpression.impression_type == ImpressionType.click
        ).scalar()
        result.append({
            "ad_id": ad.id, "title": ad.title, "shows": shows, "clicks": clicks,
            "ctr": round(clicks / shows, 4) if shows > 0 else 0, "spent": ad.spent_amount,
        })
    return result
```

- [ ] **Step 3: Register router, run tests, commit**

Add `analytics` to main.py.

```bash
cd backend && python -m pytest tests/test_api/test_analytics.py -v
```

Expected: 2 tests PASS

```bash
git add backend/
git commit -m "feat: analytics dashboard API with business metrics"
```

---

### Task 21: Seed Data Generator

**Files:**
- Create: `backend/scripts/seed_data.py`

- [ ] **Step 1: Create seed data script**

Create `backend/scripts/seed_data.py`:
```python
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base, SessionLocal, engine
from app.models import (
    Ad, AdFrequencyLevel, AdImpression, BehaviorType, BidType, Category,
    ImpressionType, Order, OrderItem, Product, Review, User, UserBehavior, UserRole,
)
from app.services.auth_service import hash_password

CATEGORIES = ["Electronics", "Clothing", "Books", "Home", "Food", "Sports", "Toys", "Beauty", "Auto", "Garden"]
PRODUCT_ADJECTIVES = ["Premium", "Budget", "Luxury", "Classic", "Modern", "Vintage", "Smart", "Eco", "Pro", "Ultra"]
PRODUCT_NOUNS = {
    "Electronics": ["Phone", "Laptop", "Tablet", "Headphones", "Camera", "Speaker", "Watch", "Monitor", "Keyboard", "Mouse"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Dress", "Sneakers", "Hat", "Scarf", "Gloves", "Socks", "Belt"],
    "Books": ["Novel", "Textbook", "Cookbook", "Biography", "Guide", "Manual", "Comic", "Dictionary", "Atlas", "Journal"],
    "Home": ["Lamp", "Chair", "Table", "Rug", "Pillow", "Curtain", "Shelf", "Clock", "Vase", "Mirror"],
    "Food": ["Coffee", "Tea", "Chocolate", "Snack Bar", "Cereal", "Pasta", "Sauce", "Spice", "Honey", "Jam"],
    "Sports": ["Ball", "Racket", "Mat", "Weights", "Bottle", "Bag", "Shoes", "Gloves", "Jersey", "Cap"],
    "Toys": ["Puzzle", "Board Game", "Doll", "Car", "Blocks", "Robot", "Kite", "Yo-Yo", "Figurine", "Plush"],
    "Beauty": ["Cream", "Serum", "Shampoo", "Lipstick", "Perfume", "Mask", "Lotion", "Oil", "Soap", "Brush"],
    "Auto": ["Charger", "Mount", "Cover", "Cleaner", "Tool Kit", "Light", "Camera", "Freshener", "Mat", "Organizer"],
    "Garden": ["Seeds", "Pot", "Shovel", "Hose", "Gloves", "Light", "Fence", "Soil", "Fertilizer", "Sprinkler"],
}
REVIEW_TEMPLATES = [
    "Great product, exactly what I needed!",
    "Good quality for the price.",
    "Decent, but could be better.",
    "Not what I expected, disappointing.",
    "Excellent! Would buy again.",
    "Average product, nothing special.",
    "Arrived damaged, poor packaging.",
    "Love it! Highly recommend.",
    "Works well, fast delivery.",
    "Okay product, fair price.",
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("Seeding categories...")
    cats = {}
    for name in CATEGORIES:
        cat = Category(name=name)
        db.add(cat)
        db.flush()
        cats[name] = cat.id

    print("Seeding users (100)...")
    users = []
    admin = User(username="admin", email="admin@example.com", hashed_password=hash_password("admin123"), role=UserRole.admin)
    db.add(admin)
    users.append(admin)

    for i in range(10):
        merchant = User(
            username=f"merchant_{i}", email=f"merchant_{i}@example.com",
            hashed_password=hash_password("merchant123"), role=UserRole.merchant,
        )
        db.add(merchant)
        users.append(merchant)

    for i in range(89):
        consumer = User(
            username=f"user_{i}", email=f"user_{i}@example.com",
            hashed_password=hash_password("user123"), role=UserRole.consumer,
            activity_score=random.uniform(0, 100),
            ad_frequency_level=random.choice(list(AdFrequencyLevel)),
        )
        db.add(consumer)
        users.append(consumer)
    db.flush()

    merchants = [u for u in users if u.role == UserRole.merchant]
    consumers = [u for u in users if u.role == UserRole.consumer]

    print("Seeding products (1000+)...")
    products = []
    for cat_name, cat_id in cats.items():
        nouns = PRODUCT_NOUNS[cat_name]
        for adj in PRODUCT_ADJECTIVES:
            for noun in nouns:
                p = Product(
                    name=f"{adj} {noun}",
                    description=f"A {adj.lower()} {noun.lower()} in the {cat_name.lower()} category.",
                    price=round(random.uniform(5.0, 500.0), 2),
                    category_id=cat_id,
                    merchant_id=random.choice(merchants).id,
                    stock=random.randint(10, 500),
                    sales_count=random.randint(0, 200),
                    tags=[cat_name.lower(), adj.lower(), noun.lower()],
                )
                db.add(p)
                products.append(p)
    db.flush()
    print(f"  Created {len(products)} products")

    print("Seeding behaviors (10000+)...")
    now = datetime.now(timezone.utc)
    behavior_types = [BehaviorType.view, BehaviorType.click, BehaviorType.cart, BehaviorType.purchase, BehaviorType.search]
    for _ in range(12000):
        user = random.choice(consumers)
        product = random.choice(products)
        btype = random.choices(behavior_types, weights=[40, 25, 15, 10, 10])[0]
        days_ago = random.uniform(0, 30)
        db.add(UserBehavior(
            user_id=user.id, product_id=product.id, behavior_type=btype,
            created_at=now - timedelta(days=days_ago),
        ))
    db.flush()

    print("Seeding reviews (500+)...")
    for _ in range(600):
        user = random.choice(consumers)
        product = random.choice(products)
        db.add(Review(
            user_id=user.id, product_id=product.id,
            rating=random.randint(1, 5),
            content=random.choice(REVIEW_TEMPLATES),
            helpful_count=random.randint(0, 20),
            created_at=now - timedelta(days=random.uniform(0, 60)),
        ))
    db.flush()

    print("Seeding orders (300+)...")
    for _ in range(350):
        user = random.choice(consumers)
        items = random.sample(products, k=random.randint(1, 4))
        total = 0
        order = Order(user_id=user.id, total_amount=0, created_at=now - timedelta(days=random.uniform(0, 30)))
        db.add(order)
        db.flush()
        for product in items:
            qty = random.randint(1, 3)
            total += product.price * qty
            db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=qty, price=product.price))
        order.total_amount = round(total, 2)
    db.flush()

    print("Seeding ads (20)...")
    ad_titles = ["Flash Sale!", "New Arrival", "Best Deal", "Limited Offer", "Top Pick",
                 "Hot Item", "Must Have", "Save Big", "Premium Quality", "Exclusive"]
    for i in range(20):
        merchant = random.choice(merchants)
        cat_name = random.choice(CATEGORIES)
        db.add(Ad(
            advertiser_id=merchant.id,
            title=f"{ad_titles[i % len(ad_titles)]} - {cat_name}",
            content=f"Check out our amazing {cat_name.lower()} deals!",
            target_url=f"/search?category={cat_name.lower()}",
            bid_amount=round(random.uniform(0.5, 5.0), 2),
            bid_type=random.choice([BidType.CPC, BidType.CPM]),
            daily_budget=round(random.uniform(50, 200), 2),
            total_budget=round(random.uniform(500, 5000), 2),
            spent_amount=round(random.uniform(0, 100), 2),
            target_tags=[cat_name.lower()],
        ))
    db.flush()

    db.commit()
    db.close()
    print("Seed complete!")


if __name__ == "__main__":
    seed()
```

- [ ] **Step 2: Run seed script**

```bash
cd backend && python scripts/seed_data.py
```

Expected: outputs seed progress and "Seed complete!"

- [ ] **Step 3: Commit**

```bash
git add backend/scripts/
git commit -m "feat: seed data generator (1000+ products, 100 users, 12000 behaviors)"
```

---

## Phase 6: Frontend

### Task 22: Vue 3 Project Setup

**Files:**
- Create: `frontend/` via Vite scaffold
- Modify: `frontend/package.json`
- Modify: `frontend/vite.config.ts`

- [ ] **Step 1: Scaffold Vue project**

```bash
cd "$(git rev-parse --show-toplevel)" && npm create vite@latest frontend -- --template vue-ts
```

- [ ] **Step 2: Install dependencies**

```bash
cd frontend && npm install && npm install element-plus @element-plus/icons-vue pinia axios vue-router@4 echarts
```

- [ ] **Step 3: Configure Vite proxy**

Replace `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: Vue 3 + Element Plus frontend scaffold"
```

---

### Task 23: Frontend Core Setup (Router, Store, API Client)

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/index.ts`
- Create: `frontend/src/stores/user.ts`
- Create: `frontend/src/router/index.ts`
- Modify: `frontend/src/main.ts`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Create API client**

Create `frontend/src/api/client.ts`:
```typescript
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

- [ ] **Step 2: Create API modules**

Create `frontend/src/api/index.ts`:
```typescript
import api from './client'

export const authApi = {
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/auth/register', data),
  login: (data: { username: string; password: string }) =>
    api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
}

export const productApi = {
  list: (page = 1) => api.get('/products', { params: { page } }),
  get: (id: number) => api.get(`/products/${id}`),
  search: (params: Record<string, any>) => api.get('/products/search', { params }),
  create: (data: any) => api.post('/products', data),
}

export const orderApi = {
  create: (items: { product_id: number; quantity: number }[]) =>
    api.post('/orders', { items }),
  list: () => api.get('/orders'),
}

export const recommendApi = {
  home: () => api.get('/recommend/home'),
  similar: (productId: number) => api.get(`/recommend/similar/${productId}`),
  forYou: () => api.get('/recommend/for-you'),
}

export const adApi = {
  fetch: () => api.get('/ads/fetch'),
  impression: (data: { ad_id: number; impression_type: string }) =>
    api.post('/ads/impression', data),
  create: (data: any) => api.post('/ads', data),
  my: () => api.get('/ads/my'),
  stats: (id: number) => api.get(`/ads/${id}/stats`),
}

export const communityApi = {
  getReviews: (productId: number) => api.get(`/reviews/product/${productId}`),
  postReview: (data: { product_id: number; rating: number; content: string }) =>
    api.post('/reviews', data),
  helpful: (reviewId: number) => api.post(`/reviews/${reviewId}/helpful`),
  getQA: (productId: number) => api.get(`/qa/product/${productId}`),
  postQuestion: (data: { product_id: number; question: string }) =>
    api.post('/qa', data),
  answer: (qaId: number, data: { answer: string }) =>
    api.post(`/qa/${qaId}/answer`, data),
}

export const activityApi = {
  myScore: () => api.get('/activity/my-score'),
}

export const behaviorApi = {
  track: (data: { product_id?: number; behavior_type: string; context?: any }) =>
    api.post('/behavior/track', data),
}

export const analyticsApi = {
  dashboard: () => api.get('/analytics/dashboard'),
  activityDist: () => api.get('/analytics/activity-dist'),
  adPerformance: () => api.get('/analytics/ad-performance'),
}
```

- [ ] **Step 3: Create user store**

Create `frontend/src/stores/user.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '../api'

export const useUserStore = defineStore('user', () => {
  const user = ref<any>(null)
  const token = ref(localStorage.getItem('token') || '')

  async function login(username: string, password: string) {
    const { data } = await authApi.login({ username, password })
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    await fetchUser()
  }

  async function register(username: string, email: string, password: string) {
    await authApi.register({ username, email, password })
    await login(username, password)
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const { data } = await authApi.me()
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
  }

  return { user, token, login, register, fetchUser, logout }
})
```

- [ ] **Step 4: Create router**

Create `frontend/src/router/index.ts`:
```typescript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/Home.vue') },
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/register', component: () => import('../views/Register.vue') },
  { path: '/product/:id', component: () => import('../views/ProductDetail.vue') },
  { path: '/search', component: () => import('../views/Search.vue') },
  { path: '/cart', component: () => import('../views/Cart.vue') },
  { path: '/orders', component: () => import('../views/Orders.vue') },
  { path: '/profile', component: () => import('../views/Profile.vue') },
  { path: '/merchant', component: () => import('../views/MerchantDashboard.vue') },
  { path: '/admin', component: () => import('../views/AdminDashboard.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

- [ ] **Step 5: Update main.ts**

Replace `frontend/src/main.ts`:
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

- [ ] **Step 6: Update App.vue with layout**

Replace `frontend/src/App.vue`:
```vue
<template>
  <el-container style="min-height: 100vh">
    <el-header>
      <el-menu mode="horizontal" :router="true" :default-active="$route.path">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/search">搜索</el-menu-item>
        <el-menu-item index="/cart" v-if="userStore.user">购物车</el-menu-item>
        <el-menu-item index="/orders" v-if="userStore.user">订单</el-menu-item>
        <el-menu-item index="/profile" v-if="userStore.user">个人中心</el-menu-item>
        <el-menu-item index="/merchant" v-if="userStore.user?.role === 'merchant'">商家后台</el-menu-item>
        <el-menu-item index="/admin" v-if="userStore.user?.role === 'admin'">管理后台</el-menu-item>
        <div style="flex-grow: 1"></div>
        <el-menu-item v-if="!userStore.user" index="/login">登录</el-menu-item>
        <el-menu-item v-if="userStore.user" @click="userStore.logout()">退出</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()
onMounted(() => userStore.fetchUser())
</script>
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/
git commit -m "feat: frontend core setup (router, pinia store, API client, layout)"
```

---

### Task 24: Frontend Pages — Login, Register, Home

**Files:**
- Create: `frontend/src/views/Login.vue`
- Create: `frontend/src/views/Register.vue`
- Create: `frontend/src/views/Home.vue`
- Create: `frontend/src/components/ProductCard.vue`
- Create: `frontend/src/components/AdBanner.vue`

- [ ] **Step 1: Create Login page**

Create `frontend/src/views/Login.vue`:
```vue
<template>
  <el-card style="max-width: 400px; margin: 40px auto">
    <template #header>用户登录</template>
    <el-form @submit.prevent="handleLogin">
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" />
      </el-form-item>
      <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">登录</el-button>
    </el-form>
    <p style="margin-top: 12px; text-align: center">
      没有账号？<router-link to="/register">注册</router-link>
    </p>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const router = useRouter()
const userStore = useUserStore()

async function handleLogin() {
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 2: Create Register page**

Create `frontend/src/views/Register.vue`:
```vue
<template>
  <el-card style="max-width: 400px; margin: 40px auto">
    <template #header>用户注册</template>
    <el-form @submit.prevent="handleRegister">
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" type="email" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" />
      </el-form-item>
      <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">注册</el-button>
    </el-form>
    <p style="margin-top: 12px; text-align: center">
      已有账号？<router-link to="/login">登录</router-link>
    </p>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const form = reactive({ username: '', email: '', password: '' })
const loading = ref(false)
const router = useRouter()
const userStore = useUserStore()

async function handleRegister() {
  loading.value = true
  try {
    await userStore.register(form.username, form.email, form.password)
    ElMessage.success('注册成功')
    router.push('/')
  } catch {
    ElMessage.error('注册失败')
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 3: Create ProductCard component**

Create `frontend/src/components/ProductCard.vue`:
```vue
<template>
  <el-card shadow="hover" style="cursor: pointer" @click="$router.push(`/product/${product.id}`)">
    <div style="padding: 14px">
      <h3 style="margin: 0 0 8px">{{ product.name }}</h3>
      <p style="color: #e74c3c; font-size: 18px; font-weight: bold; margin: 4px 0">
        ¥{{ product.price.toFixed(2) }}
      </p>
      <p style="color: #999; font-size: 12px; margin: 4px 0">销量: {{ product.sales_count }}</p>
    </div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{ product: any }>()
</script>
```

- [ ] **Step 4: Create AdBanner component**

Create `frontend/src/components/AdBanner.vue`:
```vue
<template>
  <el-card shadow="hover" style="border: 1px solid #f0ad4e; background: #fffdf5">
    <div style="display: flex; align-items: center; gap: 12px">
      <el-tag type="warning" size="small">推广</el-tag>
      <div style="flex: 1">
        <h4 style="margin: 0">{{ ad.title }}</h4>
        <p style="margin: 4px 0 0; color: #666; font-size: 13px">{{ ad.content }}</p>
      </div>
      <el-button type="warning" size="small" @click.stop="handleClick">查看详情</el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { adApi } from '../api'

const props = defineProps<{ ad: any }>()

function handleClick() {
  adApi.impression({ ad_id: props.ad.id, impression_type: 'click' })
  if (props.ad.target_url) {
    window.location.href = props.ad.target_url
  }
}
</script>
```

- [ ] **Step 5: Create Home page**

Create `frontend/src/views/Home.vue`:
```vue
<template>
  <div>
    <el-input v-model="searchQuery" placeholder="搜索商品..." size="large" style="margin-bottom: 20px"
      @keyup.enter="$router.push({ path: '/search', query: { q: searchQuery } })">
      <template #append>
        <el-button @click="$router.push({ path: '/search', query: { q: searchQuery } })">搜索</el-button>
      </template>
    </el-input>

    <h2>为你推荐</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px">
      <template v-for="(item, index) in displayItems" :key="item.type + '-' + item.data.id">
        <AdBanner v-if="item.type === 'ad'" :ad="item.data" />
        <ProductCard v-else :product="item.data" />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { recommendApi, adApi, behaviorApi } from '../api'
import ProductCard from '../components/ProductCard.vue'
import AdBanner from '../components/AdBanner.vue'

const searchQuery = ref('')
const products = ref<any[]>([])
const ads = ref<any[]>([])

const displayItems = computed(() => {
  const items: { type: string; data: any }[] = []
  let adIdx = 0
  for (let i = 0; i < products.value.length; i++) {
    items.push({ type: 'product', data: products.value[i] })
    if ((i + 1) % 4 === 0 && adIdx < ads.value.length) {
      items.push({ type: 'ad', data: ads.value[adIdx++] })
    }
  }
  return items
})

onMounted(async () => {
  try {
    const [recResp, adResp] = await Promise.all([recommendApi.home(), adApi.fetch()])
    products.value = recResp.data
    ads.value = adResp.data.ads || []
    ads.value.forEach((ad: any) => {
      adApi.impression({ ad_id: ad.id, impression_type: 'show' })
    })
  } catch { /* logged out — show empty */ }
})
</script>
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/
git commit -m "feat: login, register, home page with product grid and ad mixing"
```

---

### Task 25: Frontend Pages — Product Detail, Search, Cart, Orders

**Files:**
- Create: `frontend/src/views/ProductDetail.vue`
- Create: `frontend/src/views/Search.vue`
- Create: `frontend/src/views/Cart.vue`
- Create: `frontend/src/views/Orders.vue`
- Create: `frontend/src/stores/cart.ts`
- Create: `frontend/src/components/ReviewSection.vue`
- Create: `frontend/src/components/QASection.vue`

- [ ] **Step 1: Create cart store**

Create `frontend/src/stores/cart.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface CartItem {
  product_id: number
  name: string
  price: number
  quantity: number
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])

  const total = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  function addItem(product: { id: number; name: string; price: number }) {
    const existing = items.value.find((i) => i.product_id === product.id)
    if (existing) {
      existing.quantity++
    } else {
      items.value.push({ product_id: product.id, name: product.name, price: product.price, quantity: 1 })
    }
  }

  function removeItem(productId: number) {
    items.value = items.value.filter((i) => i.product_id !== productId)
  }

  function clear() {
    items.value = []
  }

  return { items, total, addItem, removeItem, clear }
})
```

- [ ] **Step 2: Create ReviewSection component**

Create `frontend/src/components/ReviewSection.vue`:
```vue
<template>
  <div>
    <h3>商品评价</h3>
    <el-form v-if="showForm" @submit.prevent="submitReview" style="margin-bottom: 16px">
      <el-rate v-model="newReview.rating" />
      <el-input v-model="newReview.content" type="textarea" placeholder="写下你的评价..." style="margin: 8px 0" />
      <el-button type="primary" size="small" native-type="submit">提交评价</el-button>
    </el-form>
    <div v-for="review in reviews" :key="review.id" style="border-bottom: 1px solid #eee; padding: 12px 0">
      <el-rate :model-value="review.rating" disabled />
      <p>{{ review.content }}</p>
      <el-button text size="small" @click="markHelpful(review.id)">
        有用 ({{ review.helpful_count }})
      </el-button>
    </div>
    <p v-if="reviews.length === 0" style="color: #999">暂无评价</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { communityApi } from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps<{ productId: number; showForm: boolean }>()
const reviews = ref<any[]>([])
const newReview = ref({ rating: 5, content: '' })

async function load() {
  const { data } = await communityApi.getReviews(props.productId)
  reviews.value = data
}

async function submitReview() {
  await communityApi.postReview({ product_id: props.productId, ...newReview.value })
  ElMessage.success('评价已提交')
  newReview.value = { rating: 5, content: '' }
  await load()
}

async function markHelpful(id: number) {
  await communityApi.helpful(id)
  await load()
}

onMounted(load)
</script>
```

- [ ] **Step 3: Create QASection component**

Create `frontend/src/components/QASection.vue`:
```vue
<template>
  <div>
    <h3>问答</h3>
    <el-form v-if="showForm" @submit.prevent="submitQuestion" style="margin-bottom: 16px">
      <el-input v-model="question" placeholder="提个问题..." />
      <el-button type="primary" size="small" native-type="submit" style="margin-top: 8px">提问</el-button>
    </el-form>
    <div v-for="qa in qas" :key="qa.id" style="border-bottom: 1px solid #eee; padding: 12px 0">
      <p><strong>问:</strong> {{ qa.question }}</p>
      <p v-if="qa.answer"><strong>答:</strong> {{ qa.answer }}</p>
      <p v-else style="color: #999">暂无回答</p>
    </div>
    <p v-if="qas.length === 0" style="color: #999">暂无问答</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { communityApi } from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps<{ productId: number; showForm: boolean }>()
const qas = ref<any[]>([])
const question = ref('')

async function load() {
  const { data } = await communityApi.getQA(props.productId)
  qas.value = data
}

async function submitQuestion() {
  await communityApi.postQuestion({ product_id: props.productId, question: question.value })
  ElMessage.success('问题已提交')
  question.value = ''
  await load()
}

onMounted(load)
</script>
```

- [ ] **Step 4: Create ProductDetail page**

Create `frontend/src/views/ProductDetail.vue`:
```vue
<template>
  <div v-if="product" style="max-width: 900px; margin: 0 auto">
    <el-card>
      <h1>{{ product.name }}</h1>
      <p style="color: #e74c3c; font-size: 24px; font-weight: bold">¥{{ product.price.toFixed(2) }}</p>
      <p>{{ product.description }}</p>
      <p>库存: {{ product.stock }} | 销量: {{ product.sales_count }}</p>
      <el-button type="primary" @click="addToCart">加入购物车</el-button>
    </el-card>
    <el-card style="margin-top: 16px">
      <ReviewSection :product-id="product.id" :show-form="!!userStore.user" />
    </el-card>
    <el-card style="margin-top: 16px">
      <QASection :product-id="product.id" :show-form="!!userStore.user" />
    </el-card>
    <el-card style="margin-top: 16px" v-if="similarProducts.length">
      <h3>相似商品</h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px">
        <ProductCard v-for="p in similarProducts" :key="p.id" :product="p" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { productApi, recommendApi, behaviorApi } from '../api'
import { useCartStore } from '../stores/cart'
import { useUserStore } from '../stores/user'
import ProductCard from '../components/ProductCard.vue'
import ReviewSection from '../components/ReviewSection.vue'
import QASection from '../components/QASection.vue'

const route = useRoute()
const cartStore = useCartStore()
const userStore = useUserStore()
const product = ref<any>(null)
const similarProducts = ref<any[]>([])

async function load() {
  const id = Number(route.params.id)
  const { data } = await productApi.get(id)
  product.value = data
  try {
    const simResp = await recommendApi.similar(id)
    similarProducts.value = simResp.data
    await behaviorApi.track({ product_id: id, behavior_type: 'view' })
  } catch { /* not logged in */ }
}

function addToCart() {
  cartStore.addItem(product.value)
  ElMessage.success('已加入购物车')
}

onMounted(load)
watch(() => route.params.id, load)
</script>
```

- [ ] **Step 5: Create Search page**

Create `frontend/src/views/Search.vue`:
```vue
<template>
  <div>
    <el-input v-model="query" placeholder="搜索商品..." size="large" @keyup.enter="search">
      <template #append>
        <el-button @click="search">搜索</el-button>
      </template>
    </el-input>
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; margin-top: 20px">
      <ProductCard v-for="p in products" :key="p.id" :product="p" />
    </div>
    <p v-if="searched && products.length === 0" style="color: #999; text-align: center; margin-top: 40px">
      未找到相关商品
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { productApi } from '../api'
import ProductCard from '../components/ProductCard.vue'

const route = useRoute()
const query = ref((route.query.q as string) || '')
const products = ref<any[]>([])
const searched = ref(false)

async function search() {
  const { data } = await productApi.search({ query: query.value })
  products.value = data.items || []
  searched.value = true
}

onMounted(() => { if (query.value) search() })
</script>
```

- [ ] **Step 6: Create Cart page**

Create `frontend/src/views/Cart.vue`:
```vue
<template>
  <div style="max-width: 700px; margin: 0 auto">
    <h2>购物车</h2>
    <el-table :data="cartStore.items" v-if="cartStore.items.length" style="width: 100%">
      <el-table-column prop="name" label="商品" />
      <el-table-column prop="price" label="单价" width="120">
        <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="100" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button text type="danger" @click="cartStore.removeItem(row.product_id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <p v-else style="color: #999; text-align: center; margin: 40px 0">购物车为空</p>
    <div v-if="cartStore.items.length" style="text-align: right; margin-top: 20px">
      <span style="font-size: 18px; margin-right: 20px">合计: <strong style="color: #e74c3c">¥{{ cartStore.total.toFixed(2) }}</strong></span>
      <el-button type="primary" size="large" @click="checkout">结算</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { orderApi } from '../api'
import { useCartStore } from '../stores/cart'

const cartStore = useCartStore()
const router = useRouter()

async function checkout() {
  const items = cartStore.items.map((i) => ({ product_id: i.product_id, quantity: i.quantity }))
  await orderApi.create(items)
  cartStore.clear()
  ElMessage.success('订单创建成功！')
  router.push('/orders')
}
</script>
```

- [ ] **Step 7: Create Orders page**

Create `frontend/src/views/Orders.vue`:
```vue
<template>
  <div style="max-width: 800px; margin: 0 auto">
    <h2>我的订单</h2>
    <el-card v-for="order in orders" :key="order.id" style="margin-bottom: 12px">
      <div style="display: flex; justify-content: space-between; align-items: center">
        <div>
          <p>订单号: {{ order.id }} | 状态: <el-tag :type="statusType(order.status)">{{ order.status }}</el-tag></p>
          <p>金额: <strong style="color: #e74c3c">¥{{ order.total_amount.toFixed(2) }}</strong></p>
          <p style="color: #999; font-size: 12px">{{ order.created_at }}</p>
        </div>
        <div>
          <p>{{ order.items.length }} 件商品</p>
        </div>
      </div>
    </el-card>
    <p v-if="orders.length === 0" style="color: #999; text-align: center">暂无订单</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { orderApi } from '../api'

const orders = ref<any[]>([])

function statusType(status: string) {
  const map: Record<string, string> = { pending: 'warning', paid: 'primary', shipped: 'info', completed: 'success', cancelled: 'danger' }
  return map[status] || 'info'
}

onMounted(async () => {
  const { data } = await orderApi.list()
  orders.value = data
})
</script>
```

- [ ] **Step 8: Commit**

```bash
git add frontend/src/
git commit -m "feat: product detail, search, cart, orders pages with reviews and QA"
```

---

### Task 26: Frontend Pages — Profile, Merchant, Admin Dashboards

**Files:**
- Create: `frontend/src/views/Profile.vue`
- Create: `frontend/src/views/MerchantDashboard.vue`
- Create: `frontend/src/views/AdminDashboard.vue`
- Create: `frontend/src/components/ActivityScore.vue`

- [ ] **Step 1: Create ActivityScore component**

Create `frontend/src/components/ActivityScore.vue`:
```vue
<template>
  <el-card>
    <template #header>活跃度仪表盘</template>
    <div style="text-align: center">
      <el-progress type="dashboard" :percentage="score" :color="levelColor" :width="150">
        <template #default>
          <span style="font-size: 24px; font-weight: bold">{{ score }}</span>
          <br />
          <el-tag :type="levelType">{{ levelText }}</el-tag>
        </template>
      </el-progress>
      <p style="margin-top: 12px; color: #666">广告频率等级: {{ adLevel }}</p>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { activityApi } from '../api'

const score = ref(0)
const level = ref('low')
const adLevel = ref('normal')

const levelColor = computed(() => ({ high: '#67c23a', normal: '#e6a23c', low: '#f56c6c' })[level.value] || '#409eff')
const levelType = computed(() => ({ high: 'success', normal: 'warning', low: 'danger' })[level.value] as any || 'info')
const levelText = computed(() => ({ high: '活跃用户', normal: '普通用户', low: '低活跃用户' })[level.value] || '')

onMounted(async () => {
  try {
    const { data } = await activityApi.myScore()
    score.value = Math.round(data.score)
    level.value = data.level
    adLevel.value = data.ad_frequency_level
  } catch {}
})
</script>
```

- [ ] **Step 2: Create Profile page**

Create `frontend/src/views/Profile.vue`:
```vue
<template>
  <div style="max-width: 800px; margin: 0 auto">
    <el-card style="margin-bottom: 16px">
      <template #header>个人信息</template>
      <el-descriptions :column="2" border v-if="userStore.user">
        <el-descriptions-item label="用户名">{{ userStore.user.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userStore.user.email }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ userStore.user.role }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ userStore.user.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    <ActivityScore />
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '../stores/user'
import ActivityScore from '../components/ActivityScore.vue'

const userStore = useUserStore()
</script>
```

- [ ] **Step 3: Create MerchantDashboard page**

Create `frontend/src/views/MerchantDashboard.vue`:
```vue
<template>
  <div>
    <h2>商家后台</h2>
    <el-tabs>
      <el-tab-pane label="我的广告">
        <el-button type="primary" @click="showAdForm = true" style="margin-bottom: 16px">创建广告</el-button>
        <el-dialog v-model="showAdForm" title="创建广告">
          <el-form>
            <el-form-item label="标题"><el-input v-model="adForm.title" /></el-form-item>
            <el-form-item label="内容"><el-input v-model="adForm.content" type="textarea" /></el-form-item>
            <el-form-item label="出价"><el-input-number v-model="adForm.bid_amount" :min="0.1" :step="0.1" /></el-form-item>
            <el-form-item label="日预算"><el-input-number v-model="adForm.daily_budget" :min="10" /></el-form-item>
            <el-form-item label="总预算"><el-input-number v-model="adForm.total_budget" :min="100" /></el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showAdForm = false">取消</el-button>
            <el-button type="primary" @click="createAd">创建</el-button>
          </template>
        </el-dialog>
        <el-table :data="myAds">
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="bid_amount" label="出价" width="100" />
          <el-table-column prop="spent_amount" label="已消耗" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adApi } from '../api'

const myAds = ref<any[]>([])
const showAdForm = ref(false)
const adForm = reactive({
  title: '', content: '', bid_amount: 1.0, daily_budget: 100, total_budget: 1000,
})

async function loadAds() {
  const { data } = await adApi.my()
  myAds.value = data
}

async function createAd() {
  await adApi.create(adForm)
  ElMessage.success('广告已创建')
  showAdForm.value = false
  await loadAds()
}

onMounted(loadAds)
</script>
```

- [ ] **Step 4: Create AdminDashboard page**

Create `frontend/src/views/AdminDashboard.vue`:
```vue
<template>
  <div>
    <h2>管理后台</h2>
    <el-row :gutter="16" style="margin-bottom: 20px">
      <el-col :span="6" v-for="(stat, key) in stats" :key="key">
        <el-statistic :title="stat.label" :value="stat.value" />
      </el-col>
    </el-row>

    <el-card style="margin-bottom: 16px">
      <template #header>活跃度分布</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="低活跃">{{ activityDist.low }}</el-descriptions-item>
        <el-descriptions-item label="普通">{{ activityDist.normal }}</el-descriptions-item>
        <el-descriptions-item label="高活跃">{{ activityDist.high }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card>
      <template #header>广告效果</template>
      <el-table :data="adPerf">
        <el-table-column prop="title" label="广告" />
        <el-table-column prop="shows" label="展示" width="100" />
        <el-table-column prop="clicks" label="点击" width="100" />
        <el-table-column prop="ctr" label="CTR" width="100">
          <template #default="{ row }">{{ (row.ctr * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="spent" label="消耗" width="100">
          <template #default="{ row }">¥{{ row.spent.toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { analyticsApi } from '../api'

const dashboard = ref<any>({})
const activityDist = ref({ low: 0, normal: 0, high: 0 })
const adPerf = ref<any[]>([])

const stats = computed(() => ({
  users: { label: '用户总数', value: dashboard.value.total_users || 0 },
  products: { label: '商品总数', value: dashboard.value.total_products || 0 },
  orders: { label: '订单总数', value: dashboard.value.total_orders || 0 },
  revenue: { label: '总收入 (¥)', value: dashboard.value.total_revenue || 0 },
}))

onMounted(async () => {
  const [dResp, aResp, pResp] = await Promise.all([
    analyticsApi.dashboard(),
    analyticsApi.activityDist(),
    analyticsApi.adPerformance(),
  ])
  dashboard.value = dResp.data
  activityDist.value = aResp.data
  adPerf.value = pResp.data
})
</script>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/
git commit -m "feat: profile, merchant dashboard, admin dashboard pages"
```

---

## Phase 7: Docker + Integration Tests

### Task 27: Docker Compose Setup

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`

- [ ] **Step 1: Create backend Dockerfile**

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create frontend Dockerfile**

Create `frontend/Dockerfile`:
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

Create `frontend/nginx.conf`:
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 3: Create docker-compose.yml**

Create `docker-compose.yml`:
```yaml
version: "3.8"
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/ecommerce.db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./data:/app/data
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml backend/Dockerfile frontend/Dockerfile frontend/nginx.conf
git commit -m "feat: Docker Compose setup for local deployment"
```

---

### Task 28: Integration Tests

**Files:**
- Create: `backend/tests/test_integration.py`

- [ ] **Step 1: Write integration tests**

Create `backend/tests/test_integration.py`:
```python
import pytest


def register_and_login(client, username, email, password, role=None):
    client.post("/api/auth/register", json={
        "username": username, "email": email, "password": password
    })
    if role:
        from app.database import get_db
        from app.models import User, UserRole
        db = next(client.app.dependency_overrides[get_db]())
        user = db.query(User).filter(User.username == username).first()
        user.role = UserRole(role)
        db.commit()
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def setup_full_scenario(client, db):
    from app.models import Category
    cat = Category(name="TestCat")
    db.add(cat)
    db.commit()

    merchant_h = register_and_login(client, "int_merchant", "im@t.com", "s", "merchant")
    consumer_h = register_and_login(client, "int_consumer", "ic@t.com", "s")
    admin_h = register_and_login(client, "int_admin", "ia@t.com", "s", "admin")

    # Create product
    resp = client.post("/api/products", json={
        "name": "IntProduct", "price": 50.0, "category_id": cat.id, "stock": 20
    }, headers=merchant_h)
    product_id = resp.json()["id"]

    # Create ad
    resp = client.post("/api/ads", json={
        "title": "IntAd", "bid_amount": 2.0, "daily_budget": 100, "total_budget": 500,
    }, headers=merchant_h)
    ad_id = resp.json()["id"]

    return {
        "merchant_h": merchant_h, "consumer_h": consumer_h, "admin_h": admin_h,
        "product_id": product_id, "ad_id": ad_id, "category_id": cat.id,
    }


def test_full_purchase_flow(client, setup_full_scenario):
    s = setup_full_scenario
    h = s["consumer_h"]

    # Track behavior
    client.post("/api/behavior/track", json={
        "product_id": s["product_id"], "behavior_type": "view"
    }, headers=h)

    # Add to cart and order
    resp = client.post("/api/orders", json={
        "items": [{"product_id": s["product_id"], "quantity": 2}]
    }, headers=h)
    assert resp.status_code == 201
    assert resp.json()["total_amount"] == 100.0

    # Verify orders
    resp = client.get("/api/orders", headers=h)
    assert len(resp.json()) == 1


def test_community_engagement_flow(client, setup_full_scenario):
    s = setup_full_scenario
    h = s["consumer_h"]

    # Post review
    resp = client.post("/api/reviews", json={
        "product_id": s["product_id"], "rating": 5, "content": "Great!"
    }, headers=h)
    assert resp.status_code == 201
    review_id = resp.json()["id"]

    # Mark helpful
    resp = client.post(f"/api/reviews/{review_id}/helpful", headers=h)
    assert resp.json()["helpful_count"] == 1

    # Post QA
    resp = client.post("/api/qa", json={
        "product_id": s["product_id"], "question": "Is it good?"
    }, headers=h)
    qa_id = resp.json()["id"]

    resp = client.post(f"/api/qa/{qa_id}/answer", json={"answer": "Yes!"}, headers=h)
    assert resp.json()["answer"] == "Yes!"


def test_ad_frequency_control_flow(client, setup_full_scenario):
    s = setup_full_scenario
    h = s["consumer_h"]

    # Fetch ads — should get some (new user, low activity)
    resp = client.get("/api/ads/fetch", headers=h)
    assert resp.status_code == 200
    data = resp.json()
    assert "frequency_level" in data

    # Record impression
    if data["ads"]:
        resp = client.post("/api/ads/impression", json={
            "ad_id": data["ads"][0]["id"], "impression_type": "show"
        }, headers=h)
        assert resp.status_code == 201


def test_activity_score_updates(client, setup_full_scenario):
    s = setup_full_scenario
    h = s["consumer_h"]

    # Check initial score
    resp = client.get("/api/activity/my-score", headers=h)
    initial_score = resp.json()["score"]

    # Generate activity
    for _ in range(5):
        client.post("/api/behavior/track", json={
            "product_id": s["product_id"], "behavior_type": "view"
        }, headers=h)

    # Score should increase
    resp = client.get("/api/activity/my-score", headers=h)
    assert resp.json()["score"] >= initial_score


def test_recommendation_api(client, setup_full_scenario):
    s = setup_full_scenario
    h = s["consumer_h"]

    resp = client.get("/api/recommend/home", headers=h)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    resp = client.get(f"/api/recommend/similar/{s['product_id']}", headers=h)
    assert resp.status_code == 200


def test_analytics_dashboard(client, setup_full_scenario):
    s = setup_full_scenario
    h = s["admin_h"]

    resp = client.get("/api/analytics/dashboard", headers=h)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] >= 3
    assert data["total_products"] >= 1

    resp = client.get("/api/analytics/activity-dist", headers=h)
    assert resp.status_code == 200
```

- [ ] **Step 2: Run all tests**

```bash
cd backend && python -m pytest tests/ -v --tb=short
```

Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add backend/tests/
git commit -m "test: comprehensive integration tests for all subsystems"
```

---

### Task 29: Performance Tests

**Files:**
- Create: `backend/tests/test_performance.py`

- [ ] **Step 1: Write performance tests**

Create `backend/tests/test_performance.py`:
```python
import time
import pytest
from concurrent.futures import ThreadPoolExecutor

from app.models import User, Category, Product, UserRole


@pytest.fixture
def setup_perf(client, db):
    cat = Category(name="Perf")
    merchant = User(username="perf_m", email="pm@t.com", hashed_password="h", role=UserRole.merchant)
    db.add_all([cat, merchant])
    db.commit()

    products = [Product(name=f"P{i}", price=10.0, category_id=cat.id, merchant_id=merchant.id, stock=100) for i in range(100)]
    db.add_all(products)
    db.commit()

    client.post("/api/auth/register", json={"username": "perf_u", "email": "pu@t.com", "password": "s"})
    resp = client.post("/api/auth/login", json={"username": "perf_u", "password": "s"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_recommend_response_time(client, setup_perf):
    headers = setup_perf
    times = []
    for _ in range(10):
        start = time.time()
        resp = client.get("/api/recommend/home", headers=headers)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        assert resp.status_code == 200

    avg = sum(times) / len(times)
    assert avg < 500, f"Average response time {avg:.0f}ms exceeds 500ms threshold"


def test_product_list_response_time(client, setup_perf):
    times = []
    for _ in range(10):
        start = time.time()
        resp = client.get("/api/products")
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        assert resp.status_code == 200

    avg = sum(times) / len(times)
    assert avg < 200, f"Average response time {avg:.0f}ms exceeds 200ms threshold"


def test_concurrent_requests(client, setup_perf):
    headers = setup_perf
    errors = []

    def make_request(endpoint):
        try:
            resp = client.get(endpoint, headers=headers)
            if resp.status_code != 200:
                errors.append(f"{endpoint}: status {resp.status_code}")
        except Exception as e:
            errors.append(str(e))

    endpoints = ["/api/products", "/api/recommend/home", "/api/activity/my-score"] * 10

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(make_request, endpoints)

    assert len(errors) == 0, f"Concurrent errors: {errors}"
```

- [ ] **Step 2: Run performance tests**

```bash
cd backend && python -m pytest tests/test_performance.py -v
```

Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_performance.py
git commit -m "test: performance tests (response time, concurrency)"
```

---

### Task 30: Final Verification and README

**Files:**
- Verify: all tests pass
- Create: `README.md`

- [ ] **Step 1: Run full test suite**

```bash
cd backend && python -m pytest tests/ -v --tb=short -q
```

Expected: All tests PASS (25+ tests)

- [ ] **Step 2: Verify backend starts**

```bash
cd backend && timeout 5 uvicorn app.main:app --port 8000 || true
```

Expected: Server starts without errors

- [ ] **Step 3: Commit final state**

```bash
git add -A
git commit -m "chore: final verification — all tests pass, system ready"
```
