from datetime import date, time
from enum import StrEnum

from fastapi import HTTPException, status


class MateriaOfertadaEstado(StrEnum):
    ACTIVA = "ACTIVA"
    INACTIVA = "INACTIVA"
    CERRADA = "CERRADA"
    CANCELADA = "CANCELADA"


ESTADOS_MATERIA_OFERTADA_VALIDOS = {
    MateriaOfertadaEstado.ACTIVA.value,
    MateriaOfertadaEstado.INACTIVA.value,
    MateriaOfertadaEstado.CERRADA.value,
    MateriaOfertadaEstado.CANCELADA.value,
}

ESTADOS_QUE_PERMITEN_HORARIOS = {
    MateriaOfertadaEstado.ACTIVA.value,
}


def validar_rango_fechas(fecha_inicio: date, fecha_fin: date) -> None:
    if fecha_fin < fecha_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fecha_fin no puede ser menor que fecha_inicio",
        )


def validar_rango_horas(hora_inicio: time, hora_fin: time) -> None:
    if hora_fin <= hora_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="hora_fin debe ser mayor que hora_inicio",
        )


def validar_estado_materia_ofertada(estado: str) -> None:
    if estado not in ESTADOS_MATERIA_OFERTADA_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Estado inválido. Estados permitidos: "
                "ACTIVA, INACTIVA, CERRADA, CANCELADA"
            ),
        )


def validar_materia_permite_horarios(estado: str) -> None:
    if estado not in ESTADOS_QUE_PERMITEN_HORARIOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se pueden crear o modificar horarios para una materia "
                "ofertada que no esté ACTIVA"
            ),
        )