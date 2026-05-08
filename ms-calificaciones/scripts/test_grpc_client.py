import sys
from pathlib import Path

import grpc

# Raíz del microservicio: ms-calificaciones/
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

# Carpeta donde están los archivos generados por gRPC
generated_path = project_root / "app" / "grpc" / "generated"
sys.path.append(str(generated_path))

from app.grpc.generated import calificaciones_pb2, calificaciones_pb2_grpc


def main():
    channel = grpc.insecure_channel("localhost:50054")
    stub = calificaciones_pb2_grpc.CalificacionesServiceStub(channel)

    materia_id = "11111111-1111-1111-1111-111111111111"

    response = stub.GetEstadisticasMateria(
        calificaciones_pb2.GetEstadisticasMateriaRequest(
            materia_id=materia_id,
            modo="actual",
        )
    )

    print(response)


if __name__ == "__main__":
    main()