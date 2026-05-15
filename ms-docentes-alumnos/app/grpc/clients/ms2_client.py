import grpc
import os
from app.grpc.generated import periodos_materias_pb2
from app.grpc.generated import periodos_materias_pb2_grpc

class MS2Client:
    def __init__(self):
        self.host = os.getenv("MS2_HOST", "ms-periodos-materias")
        self.port = os.getenv("MS2_PORT", "50052")
        self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = periodos_materias_pb2_grpc.PeriodosMateriasServiceStub(self.channel)

    def obtener_materia_y_periodo(self, docente_id: str, nrc_pdf: str):
        """
        Busca la materia directamente por NRC en el MS-2.
        Ya no depende de que el docente_id esté vinculado en MS-2.
        """
        try:
            request = periodos_materias_pb2.GetMateriaByNRCRequest(nrc=nrc_pdf)
            materia = self.stub.GetMateriaByNRC(request)
            
            if materia and materia.materia_ofertada_id:
                return materia.materia_ofertada_id, materia.periodo.periodo_id
            return None, None
        except Exception as e:
            print(f"Error gRPC con MS-2 (NRC {nrc_pdf}): {e}")
            return None, None