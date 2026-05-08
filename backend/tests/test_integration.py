import pytest
from app.models import User, UserRole


def register_and_login(client, username, email, password, role=None):
    client.post("/api/auth/register", json={
        "username": username, "email": email, "password": password
    })
    if role:
        from app.database import get_db
        db = next(client.app.dependency_overrides[get_db]())
        user = db.query(User).filter(User.username == username).first()
        user.role = UserRole(role)
        db.commit()
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    return {"Authorization": "Bearer " + resp.json()["access_token"]}


@pytest.fixture
def setup_full_scenario(client, db):
    from app.models import Category
    cat = Category(name="TestCat")
    db.add(cat)
    db.commit()

    merchant_h = register_and_login(client, "int_merchant", "im@t.com", "s", "merchant")
    consumer_h = register_and_login(client, "int_consumer", "ic@t.com", "s")
    admin_h = register_and_login(client, "int_admin", "ia@t.com", "s", "admin")

    resp = client.post("/api/products", json={
        "name": "IntProduct", "price": 50.0, "category_id": cat.id, "stock": 20
    }, headers=merchant_h)
    product_id = resp.json()["id"]

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

    client.post("/api/behavior/track", json={
        "product_id": s["product_id"], "behavior_type": "view"
    }, headers=h)

    resp = client.post("/api/orders", json={
        "items": [{"product_id": s["product_id"], "quantity": 2}]
    }, headers=h)
    assert resp.status_code == 201
    assert resp.json()["total_amount"] == 100.0

    resp = client.get("/api/orders", headers=h)
    assert len(resp.json()) == 1


def test_community_engagement_flow(client, setup_full_scenario):
    s = setup_full_scenario
    h = s["consumer_h"]

    resp = client.post("/api/reviews", json={
        "product_id": s["product_id"], "rating": 5, "content": "Great!"
    }, headers=h)
    assert resp.status_code == 201
    review_id = resp.json()["id"]

    resp = client.post("/api/reviews/%d/helpful" % review_id, headers=h)
    assert resp.json()["helpful_count"] == 1

    resp = client.post("/api/qa", json={
        "product_id": s["product_id"], "question": "Is it good?"
    }, headers=h)
    qa_id = resp.json()["id"]

    resp = client.post("/api/qa/%d/answer" % qa_id, json={"answer": "Yes!"}, headers=h)
    assert resp.json()["answer"] == "Yes!"


def test_ad_frequency_control_flow(client, setup_full_scenario):
    s = setup_full_scenario
    h = s["consumer_h"]

    resp = client.get("/api/ads/fetch", headers=h)
    assert resp.status_code == 200
    data = resp.json()
    assert "frequency_level" in data

    if data["ads"]:
        resp = client.post("/api/ads/impression", json={
            "ad_id": data["ads"][0]["id"], "impression_type": "show"
        }, headers=h)
        assert resp.status_code == 201


def test_activity_score_updates(client, setup_full_scenario):
    s = setup_full_scenario
    h = s["consumer_h"]

    resp = client.get("/api/activity/my-score", headers=h)
    initial_score = resp.json()["score"]

    for _ in range(5):
        client.post("/api/behavior/track", json={
            "product_id": s["product_id"], "behavior_type": "view"
        }, headers=h)

    resp = client.get("/api/activity/my-score", headers=h)
    assert resp.json()["score"] >= initial_score


def test_recommendation_api(client, setup_full_scenario):
    s = setup_full_scenario
    h = s["consumer_h"]

    resp = client.get("/api/recommend/home", headers=h)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    resp = client.get("/api/recommend/similar/%d" % s["product_id"], headers=h)
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
