from types import SimpleNamespace
from uuid import uuid4

from datetime import time

from fastapi.testclient import TestClient

from app.main import app
from app.tests.integration_helpers import create_academic_flow, get_data

from app.api.v1.endpoints import importaciones as importaciones_endpoint

def _fake_pdf_bytes() -> bytes:
    return b"%PDF-1.4\n% fake pdf content for integration test"


def _row(
    nrc: str,
    clave: str,
    materia: str,
    dia: str = "L",
    hora_inicio: str = "08:00:00",
    hora_fin: str = "10:00:00",
    salon: str = "CCO-101",
):
    profesor = "DOCENTE PDF INTEGRACION"

    return SimpleNamespace(
        nrc=nrc,
        clave=clave,
        materia=materia,
        seccion="001",
        dia=dia,
        hora_inicio=time.fromisoformat(hora_inicio),
        hora_fin=time.fromisoformat(hora_fin),
        profesor=profesor,
        docente_nombre=profesor,
        salon=salon,
    )


def _mock_parser(monkeypatch, rows):
    def fake_parse_programacion_academica_pdf(_path):
        return SimpleNamespace(
            rows=rows,
            warnings=[],
        )

    monkeypatch.setattr(
        importaciones_endpoint,
        "parse_programacion_academica_pdf",
        fake_parse_programacion_academica_pdf,
    )


def test_importar_pdf_valido_no_duplica_y_reemplaza_horarios(monkeypatch):
    with TestClient(app) as client:
        base = create_academic_flow(client)

        periodo_id = base["periodo"]["periodo_id"]
        plan_estudio_id = base["plan"]["plan_estudio_id"]

        suffix = uuid4().hex[:8]
        nrc = str(70000 + int(suffix[:4], 16) % 9999)
        clave = f"PDF-{suffix}"
        materia = f"Materia PDF {suffix}"

        _mock_parser(
            monkeypatch,
            rows=[
                _row(
                    nrc=nrc,
                    clave=clave,
                    materia=materia,
                    dia="L",
                    hora_inicio="08:00:00",
                    hora_fin="10:00:00",
                    salon="CCO-101",
                ),
                _row(
                    nrc=nrc,
                    clave=clave,
                    materia=materia,
                    dia="M",
                    hora_inicio="08:00:00",
                    hora_fin="10:00:00",
                    salon="CCO-101",
                ),
            ],
        )

        response = client.post(
            "/api/v1/importaciones/programacion-academica",
            data={
                "periodo_id": periodo_id,
                "plan_estudio_id": plan_estudio_id,
            },
            files={
                "archivo": (
                    "programacion.pdf",
                    _fake_pdf_bytes(),
                    "application/pdf",
                )
            },
        )

        assert response.status_code == 201, response.text

        _mock_parser(
            monkeypatch,
            rows=[
                _row(
                    nrc=nrc,
                    clave=clave,
                    materia=materia,
                    dia="V",
                    hora_inicio="11:00:00",
                    hora_fin="13:00:00",
                    salon="CCO-202",
                )
            ],
        )

        response = client.post(
            "/api/v1/importaciones/programacion-academica",
            data={
                "periodo_id": periodo_id,
                "plan_estudio_id": plan_estudio_id,
            },
            files={
                "archivo": (
                    "programacion.pdf",
                    _fake_pdf_bytes(),
                    "application/pdf",
                )
            },
        )

        assert response.status_code == 201, response.text

        materias = get_data(
            client.get(
                "/api/v1/materias",
                params={
                    "nrc": nrc,
                    "page": 1,
                    "limit": 10,
                },
            )
        )

        assert materias["total"] == 1

        materia_importada = materias["items"][0]

        assert materia_importada["nrc"] == nrc
        assert materia_importada["materia"]["clave"] == clave
        assert len(materia_importada["horarios"]) == 1
        assert materia_importada["horarios"][0]["dia"] == "V"
        assert materia_importada["horarios"][0]["salon"] == "CCO-202"


def test_importar_pdf_rechaza_archivo_no_pdf():
    with TestClient(app) as client:
        base = create_academic_flow(client)

        response = client.post(
            "/api/v1/importaciones/programacion-academica",
            data={
                "periodo_id": base["periodo"]["periodo_id"],
                "plan_estudio_id": base["plan"]["plan_estudio_id"],
            },
            files={
                "archivo": (
                    "programacion.txt",
                    b"esto no es un pdf",
                    "text/plain",
                )
            },
        )

        assert response.status_code == 400


def test_importar_pdf_rechaza_periodo_inexistente(monkeypatch):
    with TestClient(app) as client:
        base = create_academic_flow(client)

        _mock_parser(
            monkeypatch,
            rows=[
                _row(
                    nrc="77701",
                    clave="PDF-404P",
                    materia="Materia Periodo Inexistente",
                )
            ],
        )

        response = client.post(
            "/api/v1/importaciones/programacion-academica",
            data={
                "periodo_id": str(uuid4()),
                "plan_estudio_id": base["plan"]["plan_estudio_id"],
            },
            files={
                "archivo": (
                    "programacion.pdf",
                    _fake_pdf_bytes(),
                    "application/pdf",
                )
            },
        )

        assert response.status_code in (400, 404)


def test_importar_pdf_rechaza_plan_inexistente(monkeypatch):
    with TestClient(app) as client:
        base = create_academic_flow(client)

        _mock_parser(
            monkeypatch,
            rows=[
                _row(
                    nrc="77702",
                    clave="PDF-404PL",
                    materia="Materia Plan Inexistente",
                )
            ],
        )

        response = client.post(
            "/api/v1/importaciones/programacion-academica",
            data={
                "periodo_id": base["periodo"]["periodo_id"],
                "plan_estudio_id": str(uuid4()),
            },
            files={
                "archivo": (
                    "programacion.pdf",
                    _fake_pdf_bytes(),
                    "application/pdf",
                )
            },
        )

        assert response.status_code in (400, 404)