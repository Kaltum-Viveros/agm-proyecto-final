# Acceso a datos
from sqlalchemy.orm import Session
from app.models.notificacion import Notificacion

def crear_notificacion(db: Session, usuario_id: int, mensaje: str):
    nueva = Notificacion(
        usuario_id=usuario_id,
        mensaje=mensaje
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def obtener_notificaciones(db: Session):
    return db.query(Notificacion).all()

def obtener_por_usuario(db: Session, usuario_id: int):
    return db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id).all()