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
