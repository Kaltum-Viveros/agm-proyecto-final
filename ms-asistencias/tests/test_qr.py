import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.servicio_qr import ServicioQr

client = TestClient(app)

def test_generar_qr_valido():
    """
    Verifica que el endpoint para generar QR devuelva un token válido.
    """
    response = client.post(
        "/qr/generar",
        json={
            "id_sesion": 1,
            "id_alumno": 100,
            "matricula": "202012345"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert "expiracion" in data
    assert data["tiempo_vida_segundos"] == 20

    # Verificar que el token es descifrable por el propio servicio
    token_cifrado = data["token"]
    payload = ServicioQr.descifrar_y_validar_token(token_cifrado)
    assert payload["id_sesion"] == 1
    assert payload["id_alumno"] == 100
    assert payload["matricula"] == "202012345"
