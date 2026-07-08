def register_and_login(client, email="appuser@example.com", password="testpass123"):
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_application(client):
    headers = register_and_login(client)
    response = client.post("/applications", json={
        "company": "TestCo",
        "role": "Python Developer",
        "source": "LinkedIn",
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "TestCo"
    assert data["current_status"] == "applied"

def test_list_applications_only_shows_own(client):
    headers_a = register_and_login(client, "usera@example.com")
    headers_b = register_and_login(client, "userb@example.com")

    client.post("/applications", json={"company": "A-Corp", "role": "Dev"}, headers=headers_a)
    client.post("/applications", json={"company": "B-Corp", "role": "Dev"}, headers=headers_b)

    response = client.get("/applications", headers=headers_a)
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "A-Corp"

def test_update_status_creates_history_entry(client):
    headers = register_and_login(client)
    create_response = client.post("/applications", json={
        "company": "StatusCo", "role": "Dev",
    }, headers=headers)
    app_id = create_response.json()["id"]

    response = client.patch(f"/applications/{app_id}/status", json={
        "current_status": "interviewing",
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["current_status"] == "interviewing"

def test_cannot_access_without_auth(client):
    response = client.get("/applications")
    assert response.status_code == 403 or response.status_code == 401

def test_get_nonexistent_application_returns_404(client):
    headers = register_and_login(client)
    response = client.get("/applications/99999", headers=headers)
    assert response.status_code == 404