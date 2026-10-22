from fastapi.testclient import TestClient
from bank_system.api import app

client = TestClient(app)

def test_create_client():
    response = client.post(
        "/clients",
        json={"full_name": "Іван Франко", "email": "franko@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Іван Франко"

def test_get_nonexistent_account():
    response = client.get("/accounts/99999")
    assert response.status_code == 404