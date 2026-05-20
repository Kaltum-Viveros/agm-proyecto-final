import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.core.security import requerir_docente
from app.grpc_clients.cliente_materias import cliente_materias

client = TestClient(app)

# Mockear la dependencia del JWT
def mock_requerir_docente_valido():
    return {"id_docente": "1", "role": "DOCENTE", "user_id": "1"}

app.dependency_overrides[requerir_docente] = mock_requerir_docente_valido


@pytest.fixture
def mock_grpc_materia():
    with patch.object(cliente_materias, 'verificar_materia_docente', new_callable=AsyncMock) as mock:
        yield mock


def test_iniciar_sesion_flujo_feliz(mock_grpc_materia):
    """
    Simula que el docente tiene permiso sobre la materia (gRPC devuelve True)
    """
    mock_grpc_materia.return_value = True
    
    # Asegurarnos de limpiar cualquier sesión activa previa (simulado o apuntando a BD de prueba)
    # Por ahora simplemente probamos la ruta y esperamos 201 o 409 si ejecutamos local
    response = client.post("/sesiones/iniciar", json={"id_materia": "9999"})
    
    assert response.status_code in [201, 409] # 201 Creado o 409 si ya había en test local
    mock_grpc_materia.assert_called_once_with("9999", "1")


def test_iniciar_sesion_forbidden(mock_grpc_materia):
    """
    Simula que MS-2 rechaza la asignación de la materia
    """
    mock_grpc_materia.return_value = False
    
    response = client.post("/sesiones/iniciar", json={"id_materia": "8888"})
    
    assert response.status_code == 403
    assert "El docente no tiene asignada esta materia" in response.json()["detail"]


def test_iniciar_sesion_ms2_caido(mock_grpc_materia):
    """
    Simula que MS-2 lanza un error 503
    """
    from fastapi import HTTPException
    mock_grpc_materia.side_effect = HTTPException(status_code=503, detail="MS-2 no disponible")
    
    response = client.post("/sesiones/iniciar", json={"id_materia": "7777"})
    
    assert response.status_code == 503


def test_cerrar_sesion_con_ausentes():
    """
    Verifica que al cerrar una sesión activa se consulten los alumnos del grupo en MS-3
    y se marquen como AUSENTE a los que no asistieron.
    """
    from app.repositories.repositorio_sesiones import RepositorioSesiones
    from app.repositories.repositorio_asistencias import RepositorioAsistencias
    from app.grpc_clients.cliente_alumnos import cliente_alumnos
    from app.models.sesion_asistencia import SesionAsistencia
    from app.models.enums import EstadoSesion, EstadoAsistencia, MetodoRegistro
    from datetime import datetime, timedelta

    sesion_dummy = SesionAsistencia(
        id_sesion=120,
        id_materia="35",
        estado_sesion=EstadoSesion.ACTIVA,
        fecha_hora_fin=datetime.utcnow() + timedelta(minutes=5)
    )

    with patch.object(RepositorioSesiones, 'obtener_sesion_por_id', new_callable=AsyncMock) as mock_get_sesion, \
         patch.object(RepositorioSesiones, 'cerrar_sesion', new_callable=AsyncMock) as mock_close, \
         patch.object(cliente_alumnos, 'obtener_alumnos_por_materia', new_callable=AsyncMock) as mock_get_alumnos, \
         patch.object(RepositorioAsistencias, 'listar_asistencias_por_sesion', new_callable=AsyncMock) as mock_list_asistencias, \
         patch.object(RepositorioAsistencias, 'crear_registro_asistencia', new_callable=AsyncMock) as mock_create_asistencia:

        mock_get_sesion.return_value = sesion_dummy
        mock_close.return_value = True
        mock_get_alumnos.return_value = [
            {"id_alumno": "100", "matricula": "A100", "nombre_completo": "Juan Perez"}
        ]
        # Ningún alumno ha registrado asistencia
        mock_list_asistencias.return_value = []
        
        response = client.delete("/sesiones/120/cerrar")
        
        assert response.status_code == 200
        assert response.json()["mensaje"] == "Sesión cerrada exitosamente"
        
        # Confirmamos que se intentó crear el registro de asistencia como AUSENTE para Juan Perez
        mock_create_asistencia.assert_called_once()
        args, kwargs = mock_create_asistencia.call_args
        assert kwargs["id_alumno"] == "100"
        assert kwargs["matricula"] == "A100"
        assert kwargs["estado_asistencia"] == EstadoAsistencia.AUSENTE
        assert kwargs["metodo_registro"] == MetodoRegistro.SISTEMA

