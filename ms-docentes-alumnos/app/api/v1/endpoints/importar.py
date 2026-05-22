import grpc
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.docente import Docente
from app.services.import_service import extraer_docentes_pdf
from app.grpc.clients.auth_client import AuthClient
from app.api.deps import role_required

logger = logging.getLogger(__name__)

router = APIRouter()
auth_client = AuthClient()

@router.post("/docentes")
async def importar_docentes_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador"))
):
    contenido = await file.read()
    docentes_extraidos = extraer_docentes_pdf(contenido)

    if not docentes_extraidos:
        raise HTTPException(status_code=400, detail="No se detectaron docentes. El PDF podría tener un formato incompatible.")

    creados = 0
    omitidos_por_identidad = 0
    errores_identidad = []

    for d in docentes_extraidos:
        # Evitar duplicados por correo
        existe = db.query(Docente).filter(Docente.correo == d["correo"]).first()
        if existe:
            continue

        # Crear o reutilizar identidad en MS-1 vía gRPC.
        # Si MS-1 falla, omitimos el docente (sin fallback local).
        try:
            user_id_str, temp_pass = auth_client.crear_identidad(
                nombre=d["nombre_completo"],
                email=d["correo"],
                role="Docente"
            )
        except grpc.RpcError as e:
            logger.error(
                f"[MS-3][Docente][Importación] Fallo de conexión con MS-1. "
                f"correo={d['correo']} error={e.details()}"
            )
            omitidos_por_identidad += 1
            errores_identidad.append({
                "correo": d["correo"],
                "nombre": d["nombre_completo"],
                "detalle": f"MS-1 no disponible: {e.details()}"
            })
            continue

        if not user_id_str:
            logger.error(
                f"[MS-3][Docente][Importación] MS-1 no devolvió user_id. "
                f"correo={d['correo']}"
            )
            omitidos_por_identidad += 1
            errores_identidad.append({
                "correo": d["correo"],
                "nombre": d["nombre_completo"],
                "detalle": "MS-1 no pudo crear o reutilizar la identidad."
            })
            continue

        nuevo = Docente(
            user_id=user_id_str,
            nombre_completo=d["nombre_completo"],
            correo=d["correo"],
            cubiculo=d["cubiculo"],
            estatus_laboral=True
        )
        db.add(nuevo)
        creados += 1

    db.commit()
    return {
        "status": "success",
        "creados": creados,
        "total_leidos": len(docentes_extraidos),
        "omitidos_por_identidad": omitidos_por_identidad,
        "errores_identidad": errores_identidad
    }