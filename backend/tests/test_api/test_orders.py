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
