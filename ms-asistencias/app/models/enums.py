from enum import Enum


class EstadoSesion(str, Enum):
    ACTIVA = "ACTIVA"
    CERRADA = "CERRADA"
    EXPIRADA = "EXPIRADA"


class EstadoAsistencia(str, Enum):
    PRESENTE = "PRESENTE"
    RETARDO = "RETARDO"
    AUSENTE = "AUSENTE"


class MetodoRegistro(str, Enum):
    QR = "QR"
    SISTEMA = "SISTEMA"

class ResultadoValidacionQr(str, Enum):
    ACEPTADO = "ACEPTADO"
    RECHAZADO = "RECHAZADO"
    EXPIRADO = "EXPIRADO"
    DUPLICADO = "DUPLICADO"
