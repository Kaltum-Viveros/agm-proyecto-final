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

# NOTA: Asegúrate de tener acceso a estos modelos o prepara el gRPC [cite: 163]
# Si aún no tienes gRPC, MS-3 necesita saber a qué materia_id corresponde el NRC
# Para esta etapa, buscaremos el periodo_id y materia_id para cumplir el NOT NULL

router = APIRouter()

def normalizar_texto(texto):
    if not texto: return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    return texto.upper().replace("-", " ").strip()

@router.post("/alumnos", status_code=status.HTTP_201_CREATED)
async def importar_alumnos_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        pdf_bytes = await file.read()
        alumnos_extraidos = extraer_alumnos_buap(pdf_bytes) 
        
        alumno_repo = AlumnoRepository(Alumno)
        inscripcion_repo = InscripcionRepository(Inscripcion)
        
        todos_docentes = db.query(Docente).all()
        exitos, errores = 0, []

        for data in alumnos_extraidos:
            try:
                # 1. Búsqueda flexible del docente (ya resuelto)
                nombre_pdf_norm = normalizar_texto(data["inscripcion"]["nombre_docente"])
                palabras_pdf = set(nombre_pdf_norm.split())
                
                docente_encontrado = None
                for d in todos_docentes:
                    nombre_db_norm = normalizar_texto(d.nombre_completo)
                    if palabras_pdf.issubset(set(nombre_db_norm.split())):
                        docente_encontrado = d
                        break

                if not docente_encontrado:
                    raise Exception(f"Docente '{data['inscripcion']['nombre_docente']}' no encontrado.")

                # 2. RESOLVER MATERIA Y PERIODO (El nuevo error)
                # TODO: Implementar gRPC hacia MS-2 para obtener materia_id y periodo_id [cite: 167]
                # Por ahora, si no tienes gRPC, puedes pasar NULL si la DB lo permite
                # o buscar un ID genérico/existente para no romper el NOT NULL.
                
                materia_id = None # Aquí debe ir el UUID de MS-2
                periodo_id = None # Aquí debe ir el UUID de MS-2
                
                # --- EXPLICACIÓN  ---
                # Tu tabla 'inscripciones' tiene materia_id y periodo_id como NOT NULL.
                # Como el PDF solo tiene el NRC ('50130'), necesitas convertir ese NRC 
                # en el materia_id (UUID) que vive en el MS-2.
                # -----------------------------

                # 3. Persistir Alumno
                nuevo_alumno = alumno_repo.create_or_update(db, data["alumno"])
                
                # 4. Crear Inscripción
                # He añadido 'materia_id' y 'periodo_id' a la llamada.
                # Debes asegurarte de obtener estos UUIDs antes de este paso.
                inscripcion_repo.create(db, obj_in={
                    "alumno_id": nuevo_alumno.alumno_id,
                    "docente_id": docente_encontrado.docente_id,
                    "nrc_materia": data["inscripcion"]["nrc_materia"],
                    "materia_id": materia_id, # <--- ¡Obligatorio según tu error!
                    "periodo_id": periodo_id, # <--- ¡Obligatorio según tu error!
                    "activa": True
                })
                exitos += 1
            except Exception as e:
                db.rollback() 
                errores.append({"matricula": data["alumno"]["matricula"], "detalle": str(e)})

        return {"success": True, "summary": {"exitos": exitos, "errores": len(errores), "detalles": errores}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))