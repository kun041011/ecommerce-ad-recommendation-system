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
