from datetime import time
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.materia_horario import MateriaHorarioCreate
from app.schemas.materia_ofertada import MateriaOfertadaCreate
from app.schemas.materia_plan_estudio import MateriaPlanEstudioCreate


def test_materia_plan_estudio_create_schema():
    payload = MateriaPlanEstudioCreate(
        materia_catalogo_id=uuid4(),
        plan_estudio_id=uuid4(),
        activa=True,
    )

    assert payload.activa is True


def test_materia_ofertada_create_schema_with_docente_uuid():
    docente_id = uuid4()

    payload = MateriaOfertadaCreate(
        periodo_id=uuid4(),
        materia_catalogo_id=uuid4(),
        nrc="12345",
        seccion="001",
        docente_id=docente_id,
        docente_nombre="Dra. Ana López",
        estado="ACTIVA",
    )

    assert payload.docente_id == docente_id
    assert payload.estado == "ACTIVA"


def test_materia_horario_create_schema():
    payload = MateriaHorarioCreate(
        materia_ofertada_id=uuid4(),
        dia="LU",
        hora_inicio=time(9, 0),
        hora_fin=time(11, 0),
        salon="CCO-101",
    )

    assert payload.dia == "LU"
    assert payload.hora_inicio < payload.hora_fin


def test_materia_horario_rejects_invalid_time_range():
    with pytest.raises(ValidationError):
        MateriaHorarioCreate(
            materia_ofertada_id=uuid4(),
            dia="LU",
            hora_inicio=time(11, 0),
            hora_fin=time(9, 0),
            salon="CCO-101",
        )