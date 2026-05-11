from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services import notificacion_service
from app.schemas.notificacion_schema import NotificacionCreate, NotificacionUpdate, NotificacionResponse
from typing import List

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED, summary="Crear nueva notificación", responses={400: {"description": "Petición inválida o error de validación"}})
def crear_notificacion(data: NotificacionCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva notificación para un usuario. 
    Se utilizará el modelo NotificacionCreate para validar el payload de entrada.
    """
    return notificacion_service.crear_notificacion(db, data)

@router.get("/", response_model=List[NotificacionResponse], status_code=status.HTTP_200_OK)
def listar_notificaciones(db: Session = Depends(get_db)):
    """Obtiene una lista de todas las notificaciones registradas."""
    return notificacion_service.listar_notificaciones(db)

@router.get("/usuario/{usuario_id}", response_model=List[NotificacionResponse], status_code=status.HTTP_200_OK)
def listar_por_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtiene todas las notificaciones correspondientes a un usuario específico."""
    return notificacion_service.listar_por_usuario(db, usuario_id)

@router.get("/{notificacion_id}", response_model=NotificacionResponse, status_code=status.HTTP_200_OK, summary="Obtener notificación por ID", responses={404: {"description": "Notificación no encontrada"}})
def obtener_notificacion_por_id(notificacion_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una notificación específica a través de su ID numérico.
    Retorna un error 404 si el registro no existe en la base de datos.
    """
    return notificacion_service.obtener_por_id(db, notificacion_id)

@router.patch("/{notificacion_id}", response_model=NotificacionResponse, status_code=status.HTTP_200_OK, summary="Actualizar notificación", responses={404: {"description": "Notificación no encontrada"}, 400: {"description": "Datos de actualización inválidos"}})
def actualizar_notificacion(notificacion_id: int, data: NotificacionUpdate, db: Session = Depends(get_db)):
    """
    Actualiza parcialmente los campos de una notificación específica.
    Solo se actualizarán los campos que sean enviados en el payload.
    """
    return notificacion_service.actualizar_notificacion(db, notificacion_id, data)

@router.delete("/{notificacion_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar notificación", responses={404: {"description": "Notificación no encontrada"}})
def eliminar_notificacion(notificacion_id: int, db: Session = Depends(get_db)):
    """
    Elimina permanentemente una notificación de la base de datos.
    Esta acción no se puede deshacer.
    """
    notificacion_service.eliminar_notificacion(db, notificacion_id)
    return None