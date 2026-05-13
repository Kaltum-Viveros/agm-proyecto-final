import grpc
import logging
# from app.grpc.generated import alumnos_pb2, alumnos_pb2_grpc

class AlumnosClient:
    def __init__(self, host: str = "ms-alumnos", port: int = 50053):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None

    def _connect(self):
        if not self.channel:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            # self.stub = alumnos_pb2_grpc.AlumnoServiceStub(self.channel)

    def obtener_alumno(self, alumno_id: int) -> dict:
        """
        Llama al MS-3 para obtener los datos de un alumno dado su ID.
        Retorna un diccionario con 'email' y 'nombre'.
        """
        # TODO: Descomentar esto cuando tus compañeros agreguen alumnos.proto al monorepo
        # self._connect()
        # try:
        #     request = alumnos_pb2.GetAlumnoRequest(alumno_id=alumno_id)
        #     response = self.stub.GetAlumno(request)
        #     return {"email": response.email, "nombre": response.nombre}
        # except grpc.RpcError as e:
        #     logging.error(f"Error gRPC al consultar MS-3: {e}")
        #     return {"email": None, "nombre": None}
        
        # MOCK MIENTRAS SE CONECTAN LOS SERVICIOS:
        logging.info(f"MOCK gRPC: Consultando MS-3 por el alumno {alumno_id}")
        return {"email": "rinava404@gmail.com", "nombre": "Estudiante Prueba"}

alumnos_client = AlumnosClient()
