from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EstadoAsistencia, MetodoRegistro


class RegistrarAsistenciaRequest(BaseModel):
    """
    Datos que el dispositivo del docente envía tras escanear el QR del alumno.
    """
    token_cifrado: str = Field(..., description="El token QR generado por el dispositivo del alumno.")


class RegistroAsistenciaResponse(BaseModel):
    """
    Respuesta que se devuelve al docente al registrar la asistencia.
    """
    mensaje: str
    estado: EstadoAsistencia
    id_asistencia: int


class DetalleAsistencia(BaseModel):
    """
    Esquema para listar asistencias individuales.
    """
    id_asistencia: int
    id_sesion: int
    id_alumno: int
    matricula: str
    estado_asistencia: EstadoAsistencia
    metodo_registro: MetodoRegistro
    fecha_hora_registro: datetime

    model_config = ConfigDict(from_attributes=True)


class EstadisticasAsistenciaResponse(BaseModel):
    """
    Esquema para devolver un resumen estadístico de una clase.
    """
    total_alumnos: int
    presentes: int
    retardos: int
    ausentes: int
    porcentaje_asistencia: float
