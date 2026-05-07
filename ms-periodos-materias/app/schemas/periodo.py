from datetime import date
from uuid import UUID

# basemodel es la clase base para definir modelos de datos en pydantic, configdict se utiliza para configurar el comportamiento del modelo, y field se utiliza para definir campos con validaciones y metadatos adicionales
from pydantic import BaseModel, ConfigDict, Field 

# se define el esquema de datos para el periodo, con validaciones y tipos de datos 
class PeriodoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    fecha_inicio: date
    fecha_fin: date
    activo: bool = False

class PeriodoCreate(PeriodoBase):
    pass

# se define el esquema de datos para la actualización del periodo, con campos opcionales para permitir actualizaciones parciales
class PeriodoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    activo: bool | None = None 


class PeriodoRead(PeriodoBase):
    periodo_id: UUID

    model_config = ConfigDict(from_attributes=True) 