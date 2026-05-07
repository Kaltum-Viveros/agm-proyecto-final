from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MateriaCatalogoBase(BaseModel):
    clave: str = Field(..., min_length=1, max_length=30)
    nombre: str = Field(..., min_length=1, max_length=200)
    activo: bool = True


class MateriaCatalogoCreate(MateriaCatalogoBase):
    pass


class MateriaCatalogoUpdate(BaseModel):
    clave: str | None = Field(default=None, min_length=1, max_length=30)
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    activo: bool | None = None


class MateriaCatalogoRead(MateriaCatalogoBase):
    materia_catalogo_id: UUID

    model_config = ConfigDict(from_attributes=True)