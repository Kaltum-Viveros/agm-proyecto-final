from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime

# 1. Propiedades compartidas (Base)
class DocenteBase(BaseModel):
    nombre_completo: str
    correo: EmailStr
    cubiculo: Optional[str] = None
    horario_atencion: Optional[str] = None
    estatus_laboral: bool = True

# 2. Propiedades para crear (Lo que llega del cliente REST).
#    user_id NO se acepta desde el cliente; se obtiene desde MS-1 vía gRPC.
class DocenteCreate(DocenteBase):
    pass

# 3. Propiedades para actualizar
class DocenteUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    cubiculo: Optional[str] = None
    horario_atencion: Optional[str] = None
    estatus_laboral: Optional[bool] = None

# 4. Propiedades que se devuelven al cliente (Lo que sale de la DB)
class DocenteOut(DocenteBase):
    docente_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Esto es vital para que Pydantic pueda leer modelos de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)