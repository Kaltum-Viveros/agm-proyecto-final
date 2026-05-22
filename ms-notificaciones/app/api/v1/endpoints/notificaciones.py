from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services import notificacion_service
from app.schemas.notificacion_schema import BienvenidaRequest, BajaMateriaRequest, CierreMateriaRequest, ResetPasswordRequest, NotificacionResponse
from app.api.deps import get_current_user, role_required, roles_required

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/bienvenida", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED)
def enviar_bienvenida(
    data: BienvenidaRequest,
    db: Session = Depends(get_db),
    _user: dict = Depends(role_required("ADMIN")),  # Solo ADMIN puede disparar bienvenidas manualmente
):
    """
    Envía un correo de bienvenida a un alumno recién registrado.
    Requiere rol ADMIN.
    """
    return notificacion_service.procesar_bienvenida(db, data)

@router.post("/baja", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED)
def enviar_baja_materia(
    data: BajaMateriaRequest,
    db: Session = Depends(get_db),
    _user: dict = Depends(role_required("ADMIN")),  # Solo ADMIN puede disparar notificaciones de baja manualmente
):
    """
    Notifica al docente cuando un alumno se da de baja de una materia.
    Requiere rol ADMIN.
    """
    return notificacion_service.procesar_baja(db, data)

@router.post("/cierre-materia", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED)
def enviar_cierre_materia(
    data: CierreMateriaRequest,
    db: Session = Depends(get_db),
    _user: dict = Depends(roles_required(["ADMIN", "DOCENTE"])),  # ADMIN o DOCENTE pueden cerrar actas
):
    """
    Envía notificaciones a los alumnos de que sus actas y notas finales ya están cerradas.
    Requiere rol ADMIN o DOCENTE.
    """
    return notificacion_service.procesar_cierre_materia(db, data)

@router.post("/reset-password", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED)
def enviar_reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
    _user: dict = Depends(role_required("ADMIN")),  # Solo ADMIN puede disparar reset-password manualmente
):
    """
    Envía un correo con token temporal para restablecer la contraseña.
    Requiere rol ADMIN.
    """
    return notificacion_service.procesar_reset_password(db, data)