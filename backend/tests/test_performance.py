import time
import pytest
from app.models import User, Category, Product, UserRole


@pytest.fixture
def setup_perf(client, db):
    cat = Category(name="Perf")
    merchant = User(username="perf_m", email="pm@t.com", hashed_password="h", role=UserRole.merchant)
    db.add_all([cat, merchant])
    db.commit()

    products = [Product(name="P%d" % i, price=10.0, category_id=cat.id, merchant_id=merchant.id, stock=100) for i in range(100)]
    db.add_all(products)
    db.commit()

    client.post("/api/auth/register", json={"username": "perf_u", "email": "pu@t.com", "password": "s"})
    resp = client.post("/api/auth/login", json={"username": "perf_u", "password": "s"})
    return {"Authorization": "Bearer " + resp.json()["access_token"]}


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
    assert avg < 500, "Average response time %.0fms exceeds 500ms threshold" % avg


def test_product_list_response_time(client, setup_perf):
    times = []
    for _ in range(10):
        start = time.time()
        resp = client.get("/api/products")
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        assert resp.status_code == 200

    avg = sum(times) / len(times)
    assert avg < 200, "Average response time %.0fms exceeds 200ms threshold" % avg
