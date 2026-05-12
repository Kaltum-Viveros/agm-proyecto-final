def test_crear_notificacion(client):
    response = client.post(
        "/api/v1/notificaciones/",
        json={
            "usuario_id": 1,
            "email": "test@ejemplo.com",
            "tipo": "alerta",
            "asunto": "Asunto de prueba",
            "mensaje": "Mensaje de prueba"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@ejemplo.com"
    assert data["estado"] == "pendiente"
    assert "id" in data

def test_listar_notificaciones(client):
    response = client.get("/api/v1/notificaciones/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_error_validacion(client):
    response = client.post(
        "/api/v1/notificaciones/",
        json={
            "usuario_id": 0,  # Inválido, gt=0
            "email": "correo-invalido",
            "tipo": "a", # Inválido, min_length=2
            "asunto": "As", # Inválido, min_length=3
            "mensaje": "Msg" # Inválido, min_length=5
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "VALIDATION_ERROR"
