from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlanEstudioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150) 
    activo: bool = True


class PlanEstudioCreate(PlanEstudioBase):
    pass


class PlanEstudioUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=150)
    activo: bool | None = None


class PlanEstudioRead(PlanEstudioBase):
    plan_estudio_id: UUID

    model_config = ConfigDict(from_attributes=True)