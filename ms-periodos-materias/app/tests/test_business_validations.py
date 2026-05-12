from datetime import date, time

import pytest
from fastapi import HTTPException

from app.core.academic_rules import (
    MateriaOfertadaEstado,
    validar_estado_materia_ofertada,
    validar_materia_permite_horarios,
    validar_rango_fechas,
    validar_rango_horas,
)


def test_validar_rango_fechas_rechaza_fecha_fin_menor():
    with pytest.raises(HTTPException) as exc:
        validar_rango_fechas(
            fecha_inicio=date(2026, 8, 1),
            fecha_fin=date(2026, 7, 31),
        )

    assert exc.value.status_code == 400


def test_validar_rango_horas_rechaza_hora_fin_igual():
    with pytest.raises(HTTPException) as exc:
        validar_rango_horas(
            hora_inicio=time(10, 0),
            hora_fin=time(10, 0),
        )

    assert exc.value.status_code == 400


def test_validar_rango_horas_rechaza_hora_fin_menor():
    with pytest.raises(HTTPException) as exc:
        validar_rango_horas(
            hora_inicio=time(12, 0),
            hora_fin=time(11, 59),
        )

    assert exc.value.status_code == 400


def test_validar_estado_materia_ofertada_rechaza_estado_invalido():
    with pytest.raises(HTTPException) as exc:
        validar_estado_materia_ofertada("ABIERTA")

    assert exc.value.status_code == 400


def test_validar_estado_materia_ofertada_acepta_estados_validos():
    validar_estado_materia_ofertada(MateriaOfertadaEstado.ACTIVA.value)
    validar_estado_materia_ofertada(MateriaOfertadaEstado.INACTIVA.value)
    validar_estado_materia_ofertada(MateriaOfertadaEstado.CERRADA.value)
    validar_estado_materia_ofertada(MateriaOfertadaEstado.CANCELADA.value)


def test_validar_materia_permite_horarios_rechaza_inactiva():
    with pytest.raises(HTTPException) as exc:
        validar_materia_permite_horarios(MateriaOfertadaEstado.INACTIVA.value)

    assert exc.value.status_code == 400


def test_validar_materia_permite_horarios_rechaza_cerrada():
    with pytest.raises(HTTPException) as exc:
        validar_materia_permite_horarios(MateriaOfertadaEstado.CERRADA.value)

    assert exc.value.status_code == 400


def test_validar_materia_permite_horarios_rechaza_cancelada():
    with pytest.raises(HTTPException) as exc:
        validar_materia_permite_horarios(MateriaOfertadaEstado.CANCELADA.value)

    assert exc.value.status_code == 400


def test_validar_materia_permite_horarios_acepta_activa():
    validar_materia_permite_horarios(MateriaOfertadaEstado.ACTIVA.value)