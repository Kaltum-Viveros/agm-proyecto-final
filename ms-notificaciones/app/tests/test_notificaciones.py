def test_crear_notificacion_bienvenida(client):
    response = client.post(
        "/api/v1/notificaciones/bienvenida",
        json={
            "alumno_id": 1
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == "bienvenida"
    assert data["estado"] == "pendiente"
    assert "id" in data

def test_enviar_baja_materia(client):
    response = client.post(
        "/api/v1/notificaciones/baja",
        json={
            "alumno_id": 1,
            "docente_id": 2,
            "materia_id": 3
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == "baja_materia"

def test_error_validacion_bienvenida(client):
    response = client.post(
        "/api/v1/notificaciones/bienvenida",
        json={
            "alumno_id": 0  # Inválido, debe ser > 0
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "VALIDATION_ERROR"
