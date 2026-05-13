import grpc
import logging
# from app.grpc.generated import materias_pb2, materias_pb2_grpc

class MateriasClient:
    def __init__(self, host: str = "ms-materias", port: int = 50052):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None

    def _connect(self):
        if not self.channel:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            # self.stub = materias_pb2_grpc.MateriaServiceStub(self.channel)

    def obtener_materia(self, materia_id: int) -> dict:
        """
        Llama al MS-2 para obtener los datos de una materia.
        """
        # TODO: Descomentar esto cuando tus compañeros agreguen materias.proto
        # self._connect()
        # try:
        #     request = materias_pb2.GetMateriaRequest(materia_id=materia_id)
        #     response = self.stub.GetMateria(request)
        #     return {"nombre": response.nombre}
        # except grpc.RpcError as e:
        #     logging.error(f"Error gRPC al consultar MS-2: {e}")
        #     return {"nombre": None}
        
        # MOCK MIENTRAS SE CONECTAN LOS SERVICIOS:
        logging.info(f"MOCK gRPC: Consultando MS-2 por la materia {materia_id}")
        return {"nombre": "Programación Web Avanzada"}

materias_client = MateriasClient()
