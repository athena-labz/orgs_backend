from fastapi.testclient import TestClient

from app.main import app


# def test_health(client: TestClient):
#     response = client.get("/health")
    
#     assert response.status_code == 200
#     assert response.json() == {}