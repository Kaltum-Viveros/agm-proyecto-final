# Lógica de negocio 
from sqlalchemy.orm import Session
from app.repositories import notificacion_repository

def crear_notificacion(db: Session, data):
    return notificacion_repository.crear_notificacion(db, data)