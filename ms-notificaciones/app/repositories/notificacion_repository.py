# Acceso a datos
from sqlalchemy.orm import Session
from app.models.notificacion import Notificacion
from app.schemas.notificacion_schema import NotificacionCreate

def crear_notificacion(db: Session, data: NotificacionCreate):
    nueva = Notificacion(
        usuario_id=data.usuario_id,
        email=data.email,
        tipo=data.tipo,
        asunto=data.asunto,
        mensaje=data.mensaje
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def obtener_notificaciones(db: Session):
    return db.query(Notificacion).all()

def obtener_por_usuario(db: Session, usuario_id: int):
    return db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id).all()