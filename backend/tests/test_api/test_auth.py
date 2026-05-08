def test_register(client):
    response = client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert "id" in data


def test_register_duplicate_username(client):
    client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123"
    })
    response = client.post("/api/auth/register", json={
        "username": "alice", "email": "alice2@test.com", "password": "secret123"
    })
    assert response.status_code == 400


def test_login(client):
    client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123"
    })
    response = client.post("/api/auth/login", json={
        "username": "alice", "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123"
    })
    response = client.post("/api/auth/login", json={
        "username": "alice", "password": "wrong"
    })
    assert response.status_code == 401


def test_me(client):
    client.post("/api/auth/register", json={
        "username": "alice", "email": "alice@test.com", "password": "secret123"
    })
    login_resp = client.post("/api/auth/login", json={
        "username": "alice", "password": "secret123"
    })
    token = login_resp.json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "alice"
