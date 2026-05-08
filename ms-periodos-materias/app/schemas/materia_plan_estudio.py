from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MateriaPlanEstudioBase(BaseModel):
    materia_catalogo_id: UUID
    plan_estudio_id: UUID
    activa: bool = True


class MateriaPlanEstudioCreate(MateriaPlanEstudioBase):
    pass


class MateriaPlanEstudioUpdate(BaseModel):
    activa: bool | None = None 


class MateriaPlanEstudioRead(MateriaPlanEstudioBase):
    materia_plan_estudio_id: UUID

    model_config = ConfigDict(from_attributes=True)