# Lógica de negocio 
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.repositories import notificacion_repository
from app.schemas.notificacion_schema import NotificacionCreate, NotificacionUpdate

def crear_notificacion(db: Session, data: NotificacionCreate):
    return notificacion_repository.crear_notificacion(db, data)

def listar_notificaciones(db: Session):
    return notificacion_repository.obtener_notificaciones(db)

def listar_por_usuario(db: Session, usuario_id: int):
    return notificacion_repository.obtener_por_usuario(db, usuario_id)

def obtener_por_id(db: Session, notificacion_id: int):
    notificacion = notificacion_repository.obtener_por_id(db, notificacion_id)
    if not notificacion:
        raise NotFoundException(detail="Notificación no encontrada")
    return notificacion

def actualizar_notificacion(db: Session, notificacion_id: int, data: NotificacionUpdate):
    db_notificacion = obtener_por_id(db, notificacion_id)
    return notificacion_repository.actualizar_notificacion(db, db_notificacion, data)

def eliminar_notificacion(db: Session, notificacion_id: int):
    db_notificacion = obtener_por_id(db, notificacion_id)
    return notificacion_repository.eliminar_notificacion(db, db_notificacion)