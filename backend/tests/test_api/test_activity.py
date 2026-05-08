def test_my_activity_score(client):
    client.post("/api/auth/register", json={
        "username": "active_user", "email": "a@test.com", "password": "secret123"
    })
    resp = client.post("/api/auth/login", json={"username": "active_user", "password": "secret123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": "Bearer " + token}

    response = client.get("/api/activity/my-score", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "level" in data
    assert data["level"] in ("low", "normal", "high")
