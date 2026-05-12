from uuid import uuid4

from fastapi.testclient import TestClient


def get_data(response):
    assert response.status_code in (200, 201), response.text
    return response.json()["data"]


def deactivate_active_periods(client: TestClient) -> None:
    response = client.get(
        "/api/v1/periodos",
        params={
            "activo": True,
            "page": 1,
            "limit": 100,
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()["data"]
    items = data["items"] if isinstance(data, dict) and "items" in data else data

    for periodo in items:
        client.delete(f"/api/v1/periodos/{periodo['periodo_id']}")


def create_academic_flow(client: TestClient) -> dict:
    """
    Crea un flujo académico completo para pruebas de integración:

    periodo -> plan -> materia catálogo -> materia-plan
    -> materia ofertada -> horario
    """

    suffix = uuid4().hex[:8]
    docente_id = uuid4()
    nrc = str(80000 + int(suffix[:4], 16) % 9999)

    deactivate_active_periods(client)

    periodo = get_data(
        client.post(
            "/api/v1/periodos",
            json={
                "nombre": f"Periodo Integración {suffix}",
                "fecha_inicio": "2030-01-01",
                "fecha_fin": "2030-06-30",
                "activo": False,
            },
        )
    )

    periodo_id = periodo["periodo_id"]

    periodo_activo = get_data(
        client.patch(f"/api/v1/periodos/{periodo_id}/activar")
    )

    plan = get_data(
        client.post(
            "/api/v1/planes-estudio",
            json={
                "clave": f"PLAN-{suffix}",
                "nombre": f"Plan Integración {suffix}",
                "activo": True,
            },
        )
    )

    materia_catalogo = get_data(
        client.post(
            "/api/v1/materias-catalogo",
            json={
                "clave": f"INT-{suffix}",
                "nombre": f"Materia Integración {suffix}",
                "activo": True,
            },
        )
    )

    materia_plan = get_data(
        client.post(
            "/api/v1/materias-planes-estudio",
            json={
                "materia_catalogo_id": materia_catalogo["materia_catalogo_id"],
                "plan_estudio_id": plan["plan_estudio_id"],
                "semestre": 1,
                "activo": True,
            },
        )
    )

    materia_ofertada = get_data(
        client.post(
            "/api/v1/materias-ofertadas",
            json={
                "periodo_id": periodo_id,
                "materia_catalogo_id": materia_catalogo["materia_catalogo_id"],
                "nrc": nrc,
                "seccion": "001",
                "docente_id": str(docente_id),
                "docente_nombre": f"Docente Integración {suffix}",
                "estado": "ACTIVA",
            },
        )
    )

    horario = get_data(
        client.post(
            "/api/v1/materia-horarios",
            json={
                "materia_ofertada_id": materia_ofertada["materia_ofertada_id"],
                "dia": "L",
                "hora_inicio": "08:00:00",
                "hora_fin": "10:00:00",
                "salon": "CCO-101",
            },
        )
    )

    return {
        "suffix": suffix,
        "nrc": nrc,
        "docente_id": str(docente_id),
        "periodo": periodo_activo,
        "plan": plan,
        "materia_catalogo": materia_catalogo,
        "materia_plan": materia_plan,
        "materia_ofertada": materia_ofertada,
        "horario": horario,
    }