def test_register_new_user(client):
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "password": "testpass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data

def test_register_duplicate_email_fails(client):
    client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "testpass123",
    })
    response = client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "differentpass",
    })
    assert response.status_code == 400

def test_login_success(client):
    client.post("/auth/register", json={
        "email": "logintest@example.com",
        "password": "testpass123",
    })
    response = client.post("/auth/login", json={
        "email": "logintest@example.com",
        "password": "testpass123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password_fails(client):
    client.post("/auth/register", json={
        "email": "wrongpass@example.com",
        "password": "correctpass",
    })
    response = client.post("/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "wrongpass",
    })
    assert response.status_code == 401