import grpc
from concurrent import futures
import os
import sys

# --- EL TRUCO PARA ARREGLAR gRPC EN PYTHON ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
# Añadimos la carpeta 'generated' al path para que Python encuentre los archivos
sys.path.insert(0, os.path.join(BASE_DIR, "app", "grpc", "generated"))
# ---------------------------------------------

from app.grpc.generated import docentes_alumnos_pb2_grpc
from app.grpc.services.docente_alumno_service import DocentesAlumnosService

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    docentes_alumnos_pb2_grpc.add_DocentesAlumnosServiceServicer_to_server(
        DocentesAlumnosService(), server
    )
    server.add_insecure_port('[::]:50053')
    print(">>> Servidor gRPC MS-3 iniciado en puerto 50053")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()