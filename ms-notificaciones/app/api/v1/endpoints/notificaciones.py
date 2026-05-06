from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services import notificacion_service
from app.schemas.notificacion_schema import NotificacionCreate, NotificacionResponse
from typing import List

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=NotificacionResponse)
def crear_notificacion(data: NotificacionCreate, db: Session = Depends(get_db)):
    return notificacion_service.crear_notificacion(
        db,
        data.usuario_id,
        data.mensaje
    )

@router.get("/", response_model=List[NotificacionResponse])
def listar_notificaciones(db: Session = Depends(get_db)):
    return notificacion_service.listar_notificaciones(db)

@router.get("/{usuario_id}", response_model=List[NotificacionResponse])
def listar_por_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return notificacion_service.listar_por_usuario(db, usuario_id)