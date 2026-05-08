from datetime import time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MateriaHorarioBase(BaseModel):
    materia_ofertada_id: UUID
    dia: str = Field(..., min_length=1, max_length=2)
    hora_inicio: time
    hora_fin: time
    salon: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validar_horas(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser menor que la hora de fin")
        return self


class MateriaHorarioCreate(MateriaHorarioBase):
    pass


class MateriaHorarioUpdate(BaseModel):
    dia: str | None = Field(default=None, min_length=1, max_length=2)
    hora_inicio: time | None = None
    hora_fin: time | None = None
    salon: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validar_horas(self):
        if self.hora_inicio is not None and self.hora_fin is not None:
            if self.hora_inicio >= self.hora_fin:
                raise ValueError("La hora de inicio debe ser menor que la hora de fin")
        return self


class MateriaHorarioRead(MateriaHorarioBase):
    materia_horario_id: UUID

    model_config = ConfigDict(from_attributes=True)