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
    return {"Authorization": "Bearer " + resp.json()["access_token"]}


@pytest.fixture
def consumer_header(client):
    client.post("/api/auth/register", json={
        "username": "consumer", "email": "c@test.com", "password": "secret123"
    })
    resp = client.post("/api/auth/login", json={"username": "consumer", "password": "secret123"})
    return {"Authorization": "Bearer " + resp.json()["access_token"]}


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
