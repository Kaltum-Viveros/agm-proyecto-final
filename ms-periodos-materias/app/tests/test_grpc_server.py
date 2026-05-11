from app.grpc.generated import periodos_materias_pb2
from app.grpc.generated import periodos_materias_pb2_grpc
from app.grpc.server import serve
from app.grpc.periodos_materias_service import PeriodosMateriasGrpcService


def test_grpc_generated_modules_import_correctly():
    assert hasattr(
        periodos_materias_pb2_grpc,
        "PeriodosMateriasServiceServicer"
    )

    assert hasattr(
        periodos_materias_pb2,
        "GetMateriaByIdRequest"
    )

    assert hasattr(
        periodos_materias_pb2,
        "MateriaInfo"
    )


def test_grpc_service_can_be_instantiated():
    service = PeriodosMateriasGrpcService()

    assert service is not None


def test_grpc_server_function_exists():
    assert callable(serve)