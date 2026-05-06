# Lógica de negocio 
from sqlalchemy.orm import Session
from app.repositories import notificacion_repository

def crear_notificacion(db: Session, usuario_id: int, mensaje: str):
    return notificacion_repository.crear_notificacion(db, usuario_id, mensaje)

def listar_notificaciones(db: Session):
    return notificacion_repository.obtener_notificaciones(db)

def listar_por_usuario(db: Session, usuario_id: int):
    return notificacion_repository.obtener_por_usuario(db, usuario_id)