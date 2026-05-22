import grpc
import logging
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

logger = logging.getLogger(__name__)

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
    current_user: dict = Depends(role_required("Docente"))
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
                docente = next(
                    (d for d in todos_docentes
                     if set(nombre_pdf.split()).issubset(set(normalizar_texto(d.nombre_completo).split()))),
                    None
                )
                if not docente:
                    raise Exception(f"Docente '{nombre_pdf}' no registrado.")

                # 2. Resolver Materia/Periodo vía gRPC (MS-2)
                nrc = data["inscripcion"]["nrc_materia"]
                m_id, p_id, seccion = ms2_client.obtener_materia_y_periodo(str(docente.docente_id), nrc)
                if not m_id:
                    raise Exception(f"NRC {nrc} no hallado en MS-2.")

                # 3. Crear Identidad Real vía gRPC (MS-1).
                #    grpc.RpcError se propaga como error parcial de la fila.
                try:
                    u_id, temp_pass = auth_client.crear_identidad(
                        nombre=data["alumno"]["nombre_completo"],
                        email=data["alumno"]["correo"],
                        role="Alumno"
                    )
                except grpc.RpcError as e:
                    logger.error(
                        f"[MS-3][Alumno][Importación] Fallo de conexión con MS-1. "
                        f"correo={data['alumno']['correo']} error={e.details()}"
                    )
                    raise Exception(f"MS-1 no disponible: {e.details()}")

                if not u_id:
                    logger.error(
                        f"[MS-3][Alumno][Importación] MS-1 no devolvió user_id. "
                        f"correo={data['alumno']['correo']}"
                    )
                    raise Exception("No se pudo crear o reutilizar la identidad en MS-1.")

                # 4. Persistencia Local en MS-3 (el user_id viene de MS-1, sin fallback local).
                alumno_payload = {
                    "nombre_completo": data["alumno"]["nombre_completo"],
                    "matricula": data["alumno"]["matricula"],
                    "correo": data["alumno"]["correo"],
                    "tipo_formacion": data["alumno"].get("tipo_formacion", "Licenciatura"),
                    "estatus_academico": data["alumno"].get("estatus_academico", True),
                    "user_id": u_id,
                }
                nuevo_alumno = alumno_repo.create_or_update(db, alumno_payload)

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

                # 6. Notificación de bienvenida vía gRPC (MS-6).
                #    Solo si MS-1 devolvió contraseña temporal; no inventamos una.
                if temp_pass:
                    try:
                        notif_client.enviar_bienvenida(
                            alumno_id=nuevo_alumno.alumno_id,
                            materia_id=m_id,
                            password=temp_pass
                        )
                    except Exception as notif_err:
                        logger.warning(
                            f"[MS-3][Alumno][Importación] No se pudo enviar notificación. "
                            f"correo={data['alumno']['correo']} error={notif_err}"
                        )

                exitos += 1

            except Exception as e:
                db.rollback()
                errores.append({"matricula": data["alumno"]["matricula"], "detalle": str(e)})

        return {"success": True, "resumen": {"exitos": exitos, "errores": len(errores), "detalles": errores}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))