from fastapi import APIRouter

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

@router.get("/")
def prueba_notificaciones():
    return {"message": "Endpoint de notificaciones activo"}