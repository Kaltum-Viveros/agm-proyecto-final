# Lógica de negocio 
from sqlalchemy.orm import Session
from app.repositories import notificacion_repository
from app.schemas.notificacion_schema import NotificacionCreate

def crear_notificacion(db: Session, data: NotificacionCreate):
    return notificacion_repository.crear_notificacion(db, data)

def listar_notificaciones(db: Session):
    return notificacion_repository.obtener_notificaciones(db)

def listar_por_usuario(db: Session, usuario_id: int):
    return notificacion_repository.obtener_por_usuario(db, usuario_id)