from datetime import date, time
from uuid import uuid4

from app.schemas.materia_consulta import (
    MateriaAcademicaRead,
    MateriaCatalogoResumen,
    MateriaHorarioResumen,
    PeriodoResumen,
)


def test_materia_academica_read_schema():
    periodo = PeriodoResumen(
        periodo_id=uuid4(),
        nombre="Primavera 2026",
        fecha_inicio=date(2026, 1, 5),
        fecha_fin=date(2026, 5, 30),
        activo=True,
    )

    materia = MateriaCatalogoResumen(
        materia_catalogo_id=uuid4(),
        clave="ITIS-260",
        nombre="Servicios Web",
        activo=True,
    )

    horario = MateriaHorarioResumen(
        materia_horario_id=uuid4(),
        dia="L",
        hora_inicio=time(17, 0),
        hora_fin=time(18, 59),
        salon="CCO-101",
    )

    response = MateriaAcademicaRead(
        materia_ofertada_id=uuid4(),
        nrc="12345",
        seccion="001",
        estado="ACTIVA",
        periodo=periodo,
        materia=materia,
        docente_id=uuid4(),
        docente_nombre="Nombre del docente",
        horarios=[horario],
    )

    assert response.nrc == "12345"
    assert response.periodo.nombre == "Primavera 2026"
    assert response.materia.clave == "ITIS-260"
    assert response.horarios[0].dia == "L"