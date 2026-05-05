from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    DOCENTE = "DOCENTE"
    ALUMNO = "ALUMNO"


class TokenType(str, Enum):
    REFRESH = "REFRESH"
    PASSWORD_RESET = "PASSWORD_RESET"
    REVOKED_ACCESS = "REVOKED_ACCESS"


class TokenStatus(str, Enum):
    ACTIVE = "ACTIVE"
    USED = "USED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"