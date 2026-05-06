from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CalificacionCreate(BaseModel):
    actividad_id: UUID
    alumno_id: UUID
    calificacion: Decimal = Field(..., ge=0, le=100)
    observaciones: Optional[str] = Field(default=None, max_length=500)


class CalificacionUpdate(BaseModel):
    calificacion: Optional[Decimal] = Field(default=None, ge=0, le=100)
    observaciones: Optional[str] = Field(default=None, max_length=500)


class CalificacionResponse(BaseModel):
    id: UUID
    actividad_id: UUID
    materia_id: UUID
    alumno_id: UUID
    calificacion: Decimal
    observaciones: Optional[str]