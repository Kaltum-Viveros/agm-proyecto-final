from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PeriodoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    periodo_id: UUID
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    activo: bool


class MateriaCatalogoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    materia_catalogo_id: UUID
    clave: str
    nombre: str
    activo: bool


class MateriaHorarioResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    materia_horario_id: UUID
    dia: str
    hora_inicio: time
    hora_fin: time
    salon: str | None = None


class MateriaAcademicaRead(BaseModel):
    materia_ofertada_id: UUID
    nrc: str
    seccion: str
    estado: str
    periodo: PeriodoResumen
    materia: MateriaCatalogoResumen
    docente_id: UUID | None = None
    docente_nombre: str | None = None
    horarios: list[MateriaHorarioResumen] = []