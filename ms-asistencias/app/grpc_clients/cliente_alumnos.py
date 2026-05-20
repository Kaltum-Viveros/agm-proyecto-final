import logging

import grpc

from app.core.config import settings
from app.generated import docentes_alumnos_pb2, docentes_alumnos_pb2_grpc


class ClienteAlumnos:
    def __init__(self):
        self.target = f"{settings.ALUMNOS_GRPC_HOST}:{settings.ALUMNOS_GRPC_PORT}"
        self._channel = None
        self._stub = None
        self._loop = None

    @property
    def stub(self):
        import asyncio
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._channel is None or self._loop != current_loop:
            self._loop = current_loop
            self._channel = grpc.aio.insecure_channel(self.target)
            self._stub = docentes_alumnos_pb2_grpc.DocentesAlumnosServiceStub(self._channel)
        return self._stub

    async def verificar_alumno_en_materia(self, id_alumno: str, id_materia: str) -> bool:
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

    async def obtener_alumnos_por_materia(self, id_materia: str) -> list:
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
                    "id_alumno": alumno.alumno_id,
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

    async def obtener_docente_por_email(self, email: str) -> dict | None:
        """
        Consulta al MS-3 (Docentes) el perfil de un docente por su email.
        """
        try:
            request = docentes_alumnos_pb2.EmailRequest(email=email)
            response = await self.stub.GetDocenteByEmail(request)
            if response and response.encontrado:
                return {
                    "docente_id": response.docente_id,
                    "nombre_completo": response.nombre_completo,
                    "correo": response.correo,
                }
            return None
        except grpc.RpcError as e:
            logging.error(f"Error gRPC al conectar con MS-3 (GetDocenteByEmail): {e.details() if hasattr(e, 'details') else e}")
            return None

    async def obtener_alumno_por_email(self, email: str) -> dict | None:
        """
        Consulta al MS-3 (Alumnos) el perfil de un alumno por su email.
        """
        try:
            request = docentes_alumnos_pb2.EmailRequest(email=email)
            response = await self.stub.GetAlumnoByEmail(request)
            if response and response.alumno_id:
                return {
                    "alumno_id": response.alumno_id,
                    "nombre_completo": response.nombre_completo,
                    "matricula": response.matricula,
                    "correo": response.correo,
                }
            return None
        except grpc.RpcError as e:
            logging.error(f"Error gRPC al conectar con MS-3 (GetAlumnoByEmail): {e.details() if hasattr(e, 'details') else e}")
            return None


cliente_alumnos = ClienteAlumnos()


