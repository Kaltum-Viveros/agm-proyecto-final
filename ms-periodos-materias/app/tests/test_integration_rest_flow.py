from fastapi.testclient import TestClient

from app.main import app
from app.tests.integration_helpers import create_academic_flow, get_data


def test_rest_academic_flow_complete():
    with TestClient(app) as client:
        data = create_academic_flow(client)

        periodo_id = data["periodo"]["periodo_id"]
        docente_id = data["docente_id"]
        materia_ofertada_id = data["materia_ofertada"]["materia_ofertada_id"]

        periodo_activo = get_data(client.get("/api/v1/periodos/activo"))

        assert periodo_activo["periodo_id"] == periodo_id
        assert periodo_activo["activo"] is True

        materias_periodo = get_data(
            client.get(
                f"/api/v1/materias/periodo/{periodo_id}",
                params={"page": 1, "limit": 10},
            )
        )

        assert materias_periodo["total"] >= 1
        assert any(
            item["materia_ofertada_id"] == materia_ofertada_id
            for item in materias_periodo["items"]
        )

        materias_docente = get_data(
            client.get(
                f"/api/v1/materias/docente/{docente_id}",
                params={"page": 1, "limit": 10},
            )
        )

        assert materias_docente["total"] >= 1
        assert any(
            item["materia_ofertada_id"] == materia_ofertada_id
            for item in materias_docente["items"]
        )

        materia = get_data(
            client.get(f"/api/v1/materias/{materia_ofertada_id}")
        )

        assert materia["materia_ofertada_id"] == materia_ofertada_id
        assert materia["periodo"]["periodo_id"] == periodo_id
        assert materia["docente_id"] == docente_id
        assert len(materia["horarios"]) == 1
        assert materia["horarios"][0]["salon"] == "CCO-101"