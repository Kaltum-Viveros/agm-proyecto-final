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
        Pide las materias del docente al MS-2 y filtra por NRC.
        """
        try:
            request = periodos_materias_pb2.GetMateriasByDocenteRequest(docente_id=docente_id)
            response = self.stub.GetMateriasByDocente(request)
            
            for materia in response.materias:
                if materia.nrc == nrc_pdf:
                    # Retornamos el materia_ofertada_id y el periodo_id del contrato
                    return materia.materia_ofertada_id, materia.periodo.periodo_id
            return None, None
        except Exception as e:
            print(f"Error gRPC con MS-2: {e}")
            return None, None