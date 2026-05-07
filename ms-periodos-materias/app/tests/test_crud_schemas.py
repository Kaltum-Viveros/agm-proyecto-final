from datetime import date

from app.schemas.materia_catalogo import MateriaCatalogoCreate
from app.schemas.periodo import PeriodoCreate
from app.schemas.plan_estudio import PlanEstudioCreate


def test_periodo_create_schema():
    periodo = PeriodoCreate(
        nombre="Primavera 2026",
        fecha_inicio=date(2026, 1, 5),
        fecha_fin=date(2026, 5, 30),
        activo=True,
    )

    assert periodo.nombre == "Primavera 2026"
    assert periodo.activo is True


def test_plan_estudio_create_schema():
    plan = PlanEstudioCreate(
        nombre="Ingeniería en Tecnologías de la Información",
        activo=True,
    )

    assert plan.nombre == "Ingeniería en Tecnologías de la Información"
    assert plan.activo is True


def test_materia_catalogo_create_schema():
    materia = MateriaCatalogoCreate(
        clave="ITIS-260",
        nombre="Servicios Web",
        activo=True,
    )

    assert materia.clave == "ITIS-260"
    assert materia.nombre == "Servicios Web"