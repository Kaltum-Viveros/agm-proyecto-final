from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EstadoSesion


class IniciarSesionRequest(BaseModel):
    """
    Datos requeridos por el frontend para iniciar una sesión de clase.
    """
    id_materia: int = Field(..., description="ID de la materia para la cual se abre la sesión.")
    id_docente: int = Field(..., description="ID del docente que imparte la materia.")


class SesionResponse(BaseModel):
    """
    Respuesta que se devuelve al cliente tras crear o consultar una sesión.
    """
    id_sesion: int
    id_materia: int
    id_docente: int
    estado_sesion: EstadoSesion
    fecha_hora_inicio: datetime
    fecha_hora_limite_presente: datetime
    fecha_hora_fin: datetime
    fecha_hora_cierre: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
