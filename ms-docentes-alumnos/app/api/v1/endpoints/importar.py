import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.docente import Docente
from app.services.import_service import extraer_docentes_pdf
from app.grpc.clients.auth_client import AuthClient

router = APIRouter()
auth_client = AuthClient()

@router.post("/docentes")
async def importar_docentes_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contenido = await file.read()
    docentes_extraidos = extraer_docentes_pdf(contenido)
    
    if not docentes_extraidos:
        raise HTTPException(status_code=400, detail="No se detectaron docentes. El PDF podría tener un formato incompatible.")

    creados = 0
    for d in docentes_extraidos:
        # Evitar duplicados por correo
        existe = db.query(Docente).filter(Docente.correo == d["correo"]).first()
        if not existe:
            # Pedir a ms-auth que cree la identidad real del Docente
            user_id_str, temp_pass = auth_client.crear_identidad(
                nombre=d["nombre_completo"],
                email=d["correo"],
                role="Docente"
            )
            
            # Fallback en caso de que MS-1 falle para que no truene todo (o se podría lanzar error)
            user_id = user_id_str if user_id_str else uuid.uuid4()

            nuevo = Docente(
                user_id=user_id,
                nombre_completo=d["nombre_completo"],
                correo=d["correo"],
                cubiculo=d["cubiculo"],
                estatus_laboral=True
            )
            db.add(nuevo)
            creados += 1
    
    db.commit()
    return {"status": "success", "creados": creados, "total_leidos": len(docentes_extraidos)}