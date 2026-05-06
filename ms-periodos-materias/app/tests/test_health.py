from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_success():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["service"] == "ms-periodos-materias"
    assert body["data"]["environment"] == "development"
    assert body["data"]["status"] == "running"
    assert body["message"] == "MS-2 Periodos & Materias funcionando correctamente"