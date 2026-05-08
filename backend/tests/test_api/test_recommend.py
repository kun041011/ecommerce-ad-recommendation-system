import pytest
from app.models import User, Category, Product, UserRole


@pytest.fixture
def setup_products(db):
    user = User(username="m", email="m@t.com", hashed_password="h", role=UserRole.merchant)
    cat = Category(name="Electronics")
    db.add_all([user, cat])
    db.commit()
    for i in range(5):
        db.add(Product(name="Product %d" % i, price=10.0 + i, category_id=cat.id, merchant_id=user.id, stock=10))
    db.commit()


@pytest.fixture
def auth_header(client):
    client.post("/api/auth/register", json={
        "username": "user1", "email": "u1@t.com", "password": "s"
    })
    resp = client.post("/api/auth/login", json={"username": "user1", "password": "s"})
    return {"Authorization": "Bearer " + resp.json()["access_token"]}


def test_home_recommendations(client, auth_header, setup_products):
    response = client.get("/api/recommend/home", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_similar_products(client, auth_header, setup_products):
    response = client.get("/api/recommend/similar/1", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
