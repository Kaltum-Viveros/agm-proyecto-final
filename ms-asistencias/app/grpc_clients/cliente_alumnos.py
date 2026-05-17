import logging

import grpc

from app.core.config import settings
from app.generated import docentes_alumnos_pb2, docentes_alumnos_pb2_grpc


class ClienteAlumnos:
    def __init__(self):
        self.target = f"{settings.ALUMNOS_GRPC_HOST}:{settings.ALUMNOS_GRPC_PORT}"
        self.channel = grpc.aio.insecure_channel(self.target)
        self.stub = docentes_alumnos_pb2_grpc.DocentesAlumnosServiceStub(self.channel)

    async def verificar_alumno_en_materia(self, id_alumno: int, id_materia: int) -> bool:
        """
        Consulta al MS-3 (Alumnos) si el alumno está inscrito en esta materia.
        """
        try:
            request = docentes_alumnos_pb2.RelationRequest(
                alumno_id=str(id_alumno),
                materia_id=str(id_materia)
            )
            response = await self.stub.IsAlumnoEnMateria(request)
            return response.exists
        except grpc.RpcError as e:
            logging.error(f"Error gRPC al conectar con MS-3 (Alumnos): {e.details() if hasattr(e, 'details') else e}")
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio de alumnos no está disponible actualmente."
            )

    async def obtener_alumnos_por_materia(self, id_materia: int) -> list:
        """
        Consulta al MS-3 (Alumnos) todos los alumnos inscritos en esta materia.
        """
        try:
            request = docentes_alumnos_pb2.GetAlumnosRequest(
                materia_id=str(id_materia)
            )
            response = await self.stub.GetAlumnosByMateria(request)
            return [
                {
                    "id_alumno": int(alumno.alumno_id),
                    "matricula": alumno.matricula,
                    "nombre_completo": alumno.nombre_completo
                }
                for alumno in response.alumnos
            ]
        except grpc.RpcError as e:
            logging.error(f"Error gRPC al obtener alumnos de MS-3: {e.details() if hasattr(e, 'details') else e}")
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio de alumnos no está disponible actualmente."
            )


cliente_alumnos = ClienteAlumnos()

