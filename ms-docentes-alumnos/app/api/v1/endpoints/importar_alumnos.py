import unicodedata
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.import_service_alumno import extraer_alumnos_buap 
from app.repositories.alumno_repository import AlumnoRepository
from app.repositories.inscripcion_repository import InscripcionRepository
from app.models.alumno import Alumno
from app.models.inscripcion import Inscripcion
from app.models.docente import Docente

# Clientes gRPC y Seguridad
from app.grpc.clients.ms2_client import MS2Client
from app.grpc.clients.auth_client import AuthClient
from app.grpc.clients.notif_client import NotifClient
from app.api.deps import role_required

router = APIRouter()
ms2_client = MS2Client()
auth_client = AuthClient()
notif_client = NotifClient()

def normalizar_texto(t):
    if not t: return ""
    t = unicodedata.normalize('NFD', t).encode('ascii', 'ignore').decode("utf-8")
    return t.upper().replace("-", " ").strip()

@router.post("/alumnos", status_code=status.HTTP_201_CREATED)
async def importar_alumnos_pdf(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    # Seguridad: Solo el Docente accede
    docente = Depends(role_required("Docente"))
):
    try:
        pdf_bytes = await file.read()
        alumnos_extraidos = extraer_alumnos_buap(pdf_bytes) 
        
        alumno_repo = AlumnoRepository(Alumno)
        inscripcion_repo = InscripcionRepository(Inscripcion)
        todos_docentes = db.query(Docente).all()
        exitos, errores = 0, []

        for data in alumnos_extraidos:
            try:
                # 1. Resolver Docente Local
                nombre_pdf = normalizar_texto(data["inscripcion"]["nombre_docente"])
                docente = next((d for d in todos_docentes if set(nombre_pdf.split()).issubset(set(normalizar_texto(d.nombre_completo).split()))), None)
                if not docente: raise Exception(f"Docente '{nombre_pdf}' no registrado.")

                # 2. Resolver Materia/Periodo vía gRPC (MS-2)
                nrc = data["inscripcion"]["nrc_materia"]
                m_id, p_id, seccion = ms2_client.obtener_materia_y_periodo(str(docente.docente_id), nrc)
                if not m_id: raise Exception(f"NRC {nrc} no hallado en MS-2.")

                # 3. Crear Identidad Real vía gRPC (MS-1)
                u_id, temp_pass = auth_client.crear_identidad(
                    nombre=data["alumno"]["nombre_completo"],
                    email=data["alumno"]["correo"],
                    role="Alumno"
                )
                if not u_id: raise Exception("No se pudo crear el usuario en MS-1.")
                
                # 4. Persistencia Local en MS-3
                data["alumno"]["user_id"] = u_id
                nuevo_alumno = alumno_repo.create_or_update(db, data["alumno"])
                
                # 5. Inscripción — verificar idempotencia antes de insertar
                ya_inscrito = db.query(Inscripcion).filter(
                    Inscripcion.alumno_id == nuevo_alumno.alumno_id,
                    Inscripcion.materia_id == m_id,
                    Inscripcion.activa == True
                ).first()

                if not ya_inscrito:
                    inscripcion_repo.create(db, obj_in={
                        "alumno_id": nuevo_alumno.alumno_id,
                        "docente_id": docente.docente_id,
                        "nrc_materia": nrc,
                        "materia_id": m_id,
                        "periodo_id": p_id,
                        "seccion_materia": seccion,
                        "activa": True
                    })

                # 6. Notificación de bienvenida vía gRPC (MS-6)
                notif_client.enviar_bienvenida(
                    alumno_id=nuevo_alumno.alumno_id,
                    materia_id=m_id,
                    password=temp_pass
                )

                exitos += 1
            except Exception as e:
                db.rollback()
                errores.append({"matricula": data["alumno"]["matricula"], "detalle": str(e)})

        return {"success": True, "resumen": {"exitos": exitos, "errores": len(errores), "detalles": errores}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))