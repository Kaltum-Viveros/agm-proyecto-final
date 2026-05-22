"""
Cliente gRPC hacia MS-Docentes-Alumnos (MS-3).
Permite al MS-2 verificar si un docente existe antes de asignarlo a una materia.
"""
import grpc
import logging
from app.core.config import settings

try:
    from app.grpc.generated import docentes_alumnos_pb2, docentes_alumnos_pb2_grpc
    _PROTO_AVAILABLE = True
except ImportError:
    _PROTO_AVAILABLE = False
    logging.warning("docentes_alumnos_pb2 no disponible. Ejecuta compile_all_protos.py")


class DocentesClient:
    """Cliente gRPC sincrónico hacia MS-Docentes-Alumnos."""

    def __init__(self):
        self._channel = None
        self._stub = None

    def _get_stub(self):
        if not _PROTO_AVAILABLE:
            return None
        if self._stub is None:
            host = settings.ms_docentes_alumnos_grpc_host
            port = settings.ms_docentes_alumnos_grpc_port
            self._channel = grpc.insecure_channel(f"{host}:{port}")
            self._stub = docentes_alumnos_pb2_grpc.DocentesAlumnosServiceStub(self._channel)
        return self._stub

    def verificar_docente(self, docente_id: str) -> bool:
        """
        Consulta al MS-3 para verificar si un docente existe y está activo.
        Retorna True si existe y es válido, False en caso contrario.
        """
        stub = self._get_stub()
        if not stub:
            logging.warning("[DocentesClient] Proto no disponible, omitiendo verificación.")
            return False
        try:
            request = docentes_alumnos_pb2.DocenteIdRequest(docente_id=docente_id)
            response = stub.GetDocenteById(request)
            if response and response.encontrado:
                return True
            return False
        except grpc.RpcError as e:
            logging.error(f"[DocentesClient] Error gRPC al verificar docente {docente_id}: {e.details()}")
            return False

    def resolver_docente_por_nombre(self, nombre_completo: str) -> str | None:
        """
        Busca el UUID del docente en MS-3 a partir del nombre extraído del PDF.
        Retorna el docente_id como string UUID, o None si no se encontró.
        """
        stub = self._get_stub()
        if not stub:
            logging.warning("[DocentesClient] Proto no disponible, no se puede resolver docente por nombre.")
            return None
        try:
            request = docentes_alumnos_pb2.DocenteNombreRequest(nombre_completo=nombre_completo)
            response = stub.GetDocenteByNombre(request)
            if response.encontrado:
                logging.info(f"[DocentesClient] Docente '{nombre_completo}' resuelto → {response.docente_id}")
                return response.docente_id
            logging.warning(f"[DocentesClient] Docente '{nombre_completo}' no encontrado en MS-3")
            return None
        except grpc.RpcError as e:
            logging.error(f"[DocentesClient] Error gRPC al resolver docente por nombre: {e.details()}")
            return None


# Instancia singleton
docentes_client = DocentesClient()
