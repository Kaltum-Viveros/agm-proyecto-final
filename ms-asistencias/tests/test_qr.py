import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.core.security import requerir_alumno
from app.grpc_clients.cliente_alumnos import cliente_alumnos
from app.repositories.repositorio_sesiones import RepositorioSesiones
from app.models.sesion_asistencia import SesionAsistencia
from app.models.enums import EstadoSesion
from datetime import datetime, timedelta

client = TestClient(app)

def mock_requerir_alumno_valido():
    return {"id_alumno": "27", "role": "ALUMNO", "user_id": "27", "matricula": "A01234567"}

app.dependency_overrides[requerir_alumno] = mock_requerir_alumno_valido


@pytest.fixture
def mock_grpc_alumno():
    with patch.object(cliente_alumnos, 'verificar_alumno_en_materia', new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_sesion_activa():
    with patch.object(RepositorioSesiones, 'obtener_sesion_por_id', new_callable=AsyncMock) as mock:
        # Devolvemos una sesión dummy
        sesion = SesionAsistencia(
            id_sesion=15,
            id_materia="35",
            estado_sesion=EstadoSesion.ACTIVA,
            fecha_hora_fin=datetime.utcnow() + timedelta(minutes=5)
        )
        mock.return_value = sesion
        yield mock


def test_generar_qr_flujo_feliz(mock_grpc_alumno, mock_sesion_activa):
    mock_grpc_alumno.return_value = True
    
    response = client.post("/qr/generar", json={"id_sesion": 15})
    
    assert response.status_code == 201
    assert "token" in response.json()
    mock_grpc_alumno.assert_called_once_with("27", "35")


def test_generar_qr_forbidden(mock_grpc_alumno, mock_sesion_activa):
    mock_grpc_alumno.return_value = False
    
    response = client.post("/qr/generar", json={"id_sesion": 15})
    
    assert response.status_code == 403
    assert "no está inscrito" in response.json()["detail"]


def test_generar_qr_sesion_no_existe(mock_grpc_alumno):
    with patch.object(RepositorioSesiones, 'obtener_sesion_por_id', new_callable=AsyncMock) as mock_sesion:
        mock_sesion.return_value = None
        response = client.post("/qr/generar", json={"id_sesion": 999})
        assert response.status_code == 404
