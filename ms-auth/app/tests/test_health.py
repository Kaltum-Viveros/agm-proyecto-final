from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_success_response() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "MS Auth funcionando correctamente"
    assert body["data"]["service"] == "ms-auth"
    assert body["data"]["status"] == "ok"