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
    return {"Authorization": "Bearer " + resp.json()["access_token"]}


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
