import pytest
import grpc
import grpc.aio

from app.generated import asistencias_pb2
from app.generated import asistencias_pb2_grpc

@pytest.mark.asyncio
async def test_get_asistencia_alumno():
    """
    Prueba que el servidor gRPC entrante esté escuchando en el puerto 50055
    y pueda procesar la solicitud GetAsistenciaAlumno.
    """
    # Como el servidor gRPC está corriendo en segundo plano dentro de Docker en el puerto 50055
    # Nos conectamos a localhost:50055
    async with grpc.aio.insecure_channel("localhost:50055") as channel:
        stub = asistencias_pb2_grpc.AsistenciasServiceStub(channel)
        
        request = asistencias_pb2.AsistenciaAlumnoRequest(
            id_alumno=100,
            id_materia=1
        )
        
        try:
            response = await stub.GetAsistenciaAlumno(request)
            
            # Debería retornar una lista vacía o valores por defecto
            # ya que la BD local probablemente no tiene asistencias para el alumno 100
            assert response is not None
            assert hasattr(response, 'total_presentes')
            assert hasattr(response, 'total_retardos')
        except grpc.RpcError as e:
            # Si el servicio aún no arranca o hay problemas de DB,
            # capturamos el RpcError pero confirmamos que la conexión sí se estableció
            pytest.fail(f"La llamada gRPC falló: {e.details()}")
