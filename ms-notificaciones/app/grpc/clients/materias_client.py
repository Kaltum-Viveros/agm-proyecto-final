import grpc
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))

try:
    from app.grpc.generated import periodos_materias_pb2, periodos_materias_pb2_grpc
except ImportError:
    pass

from app.core.config import settings

class MateriasClient:
    def __init__(self):
        self._channel = None
        self._stub = None

    def _get_stub(self):
        if self._stub is None:
            host = settings.ms_periodos_materias_grpc_host
            port = settings.ms_periodos_materias_grpc_port
            self._channel = grpc.insecure_channel(f"{host}:{port}")
            if 'periodos_materias_pb2_grpc' in globals():
                self._stub = periodos_materias_pb2_grpc.PeriodosMateriasServiceStub(self._channel)
        return self._stub

    def obtener_materia(self, materia_id: str) -> dict:
        """
        Llama al MS-2 para obtener los datos de una materia.
        """
        stub = self._get_stub()
        if not stub:
            logging.error(
                "No se pudo crear stub gRPC de MS-2 Periodos/Materias; no se usara materia mock."
            )
            return {
                "nombre": "",
                "found": False,
                "error_code": "PERIODOS_GRPC_STUB_UNAVAILABLE",
                "message": "No se pudo consultar la materia por gRPC",
            }
        try:
            request = periodos_materias_pb2.GetMateriaByIdRequest(materia_id=str(materia_id))
            response = stub.GetMateriaById(request)
            nombre = ""
            if response.HasField("materia"):
                nombre = response.materia.nombre
            return {
                "nombre": nombre,
                "found": bool(nombre),
                "materia_id": getattr(response, "materia_ofertada_id", str(materia_id)),
                "nrc": getattr(response, "nrc", ""),
            }
        except Exception as e:
            logging.error(f"Error gRPC al consultar MS-2: {e}")
            return {
                "nombre": "",
                "found": False,
                "error_code": "PERIODOS_GRPC_ERROR",
                "message": "No se pudo consultar la materia por gRPC",
            }

materias_client = MateriasClient()
