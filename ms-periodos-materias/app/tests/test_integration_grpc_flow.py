from uuid import uuid4

import grpc
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.grpc.generated import periodos_materias_pb2
from app.grpc.generated import periodos_materias_pb2_grpc
from app.grpc.periodos_materias_service import PeriodosMateriasGrpcService
from app.main import app
from app.tests.integration_helpers import create_academic_flow


@pytest_asyncio.fixture
async def grpc_stub():
    server = grpc.aio.server()

    periodos_materias_pb2_grpc.add_PeriodosMateriasServiceServicer_to_server(
        PeriodosMateriasGrpcService(),
        server,
    )

    port = server.add_insecure_port("127.0.0.1:0")

    await server.start()

    channel = grpc.aio.insecure_channel(f"127.0.0.1:{port}")
    stub = periodos_materias_pb2_grpc.PeriodosMateriasServiceStub(channel)

    try:
        yield stub
    finally:
        await channel.close()
        await server.stop(0)


@pytest.fixture
def academic_flow_data():
    with TestClient(app) as client:
        return create_academic_flow(client)


@pytest.mark.asyncio
async def test_grpc_get_periodo_activo(grpc_stub, academic_flow_data):
    response = await grpc_stub.GetPeriodoActivo(
        periodos_materias_pb2.GetPeriodoActivoRequest()
    )

    assert response.periodo_id == academic_flow_data["periodo"]["periodo_id"]
    assert response.activo is True


@pytest.mark.asyncio
async def test_grpc_get_materia_by_id_correcto(grpc_stub, academic_flow_data):
    materia_ofertada_id = academic_flow_data["materia_ofertada"]["materia_ofertada_id"]

    response = await grpc_stub.GetMateriaById(
        periodos_materias_pb2.GetMateriaByIdRequest(
            materia_id=materia_ofertada_id,
        )
    )

    assert response.materia_ofertada_id == materia_ofertada_id
    assert response.nrc == academic_flow_data["nrc"]
    assert response.periodo.periodo_id == academic_flow_data["periodo"]["periodo_id"]
    assert response.materia.materia_catalogo_id == academic_flow_data["materia_catalogo"]["materia_catalogo_id"]


@pytest.mark.asyncio
async def test_grpc_get_materia_by_id_not_found(grpc_stub):
    with pytest.raises(grpc.aio.AioRpcError) as exc_info:
        await grpc_stub.GetMateriaById(
            periodos_materias_pb2.GetMateriaByIdRequest(
                materia_id=str(uuid4()),
            )
        )

    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND


@pytest.mark.asyncio
async def test_grpc_get_materias_by_docente_correcto(grpc_stub, academic_flow_data):
    response = await grpc_stub.GetMateriasByDocente(
        periodos_materias_pb2.GetMateriasByDocenteRequest(
            docente_id=academic_flow_data["docente_id"],
        )
    )

    assert len(response.materias) >= 1

    materia_ids = [materia.materia_ofertada_id for materia in response.materias]

    assert academic_flow_data["materia_ofertada"]["materia_ofertada_id"] in materia_ids


@pytest.mark.asyncio
async def test_grpc_get_materias_by_docente_lista_vacia(grpc_stub):
    response = await grpc_stub.GetMateriasByDocente(
        periodos_materias_pb2.GetMateriasByDocenteRequest(
            docente_id=str(uuid4()),
        )
    )

    assert len(response.materias) == 0