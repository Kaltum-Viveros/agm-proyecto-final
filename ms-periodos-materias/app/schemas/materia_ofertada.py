from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MateriaOfertadaBase(BaseModel):
    periodo_id: UUID
    materia_catalogo_id: UUID
    nrc: str = Field(..., min_length=1, max_length=5)
    seccion: str = Field(..., min_length=1, max_length=100)
    docente_id: UUID | None = None
    docente_nombre: str | None = Field(default=None, max_length=100)
    estado: str = Field(default="ACTIVA", min_length=1, max_length=30)


class MateriaOfertadaCreate(MateriaOfertadaBase):
    pass


class MateriaOfertadaUpdate(BaseModel):
    periodo_id: UUID | None = None
    materia_catalogo_id: UUID | None = None
    nrc: str | None = Field(default=None, min_length=1, max_length=5)
    seccion: str | None = Field(default=None, min_length=1, max_length=100)
    docente_id: UUID | None = None
    docente_nombre: str | None = Field(default=None, max_length=100)
    estado: str | None = Field(default=None, min_length=1, max_length=30)


class MateriaOfertadaRead(MateriaOfertadaBase):
    materia_ofertada_id: UUID

    model_config = ConfigDict(from_attributes=True)