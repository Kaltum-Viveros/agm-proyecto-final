from datetime import datetime

from pydantic import BaseModel, Field


class GenerarQrRequest(BaseModel):
    """
    Datos que el dispositivo del alumno envía para obtener un QR válido.
    """
    id_sesion: int = Field(..., description="ID de la sesión activa de la clase.")


class GenerarQrResponse(BaseModel):
    """
    El token cifrado que el dispositivo del alumno mostrará en pantalla.
    """
    token: str = Field(..., description="String cifrado en Base64 con el payload del QR.")
    expiracion: datetime = Field(..., description="Momento exacto en que este token dejará de ser válido.")
    tiempo_vida_segundos: int = Field(..., description="Segundos que el token permanece vivo (TTL).")
