import pytest
from app.models.user import UserRole


@pytest.fixture
def merchant_token(client):
    client.post("/api/auth/register", json={
        "username": "merchant", "email": "m@test.com", "password": "secret123"
    })
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
