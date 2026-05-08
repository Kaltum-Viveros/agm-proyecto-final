# Acceso a datos
from sqlalchemy.orm import Session
from app.models.notificacion import Notificacion
from app.schemas.notificacion_schema import NotificacionCreate, NotificacionUpdate

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

def obtener_por_id(db: Session, notificacion_id: int):
    return db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()

def actualizar_notificacion(db: Session, db_notificacion: Notificacion, data: NotificacionUpdate):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_notificacion, key, value)
    db.commit()
    db.refresh(db_notificacion)
    return db_notificacion

def eliminar_notificacion(db: Session, db_notificacion: Notificacion):
    db.delete(db_notificacion)
    db.commit()
    return db_notificacion