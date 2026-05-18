from fastapi import HTTPException
from app.grpc.clients import periodos_materias_client, docentes_alumnos_client, calificaciones_client
from app.services.pdf_generator import generate_calificaciones_pdf
from app.services.excel_generator import generate_calificaciones_excel
from app.repositories.reporte_repository import ReporteRepository
import uuid

class ReporteService:
    def __init__(self, repository: ReporteRepository):
        self.repository = repository

    async def generar_reporte_calificaciones(self, materia_id: str, formato: str):
        if formato not in ["pdf", "xlsx"]:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use 'pdf' o 'xlsx'.")

        # 1. Consultar materia_id en MS-2
        materia_res = periodos_materias_client.get_materia_by_id(materia_id)
        if not materia_res or not materia_res.materia_ofertada_id:
            raise HTTPException(status_code=404, detail="Materia no encontrada en MS-2 (Periodos y Materias).")

        # Parsear a diccionario para uso fácil
        materia_data = {
            "materia_ofertada_id": materia_res.materia_ofertada_id,
            "nrc": materia_res.nrc,
            "seccion": materia_res.seccion,
            "nombre": materia_res.materia.nombre if materia_res.HasField("materia") else "N/A",
            "docente_id": materia_res.docente_id,
            "docente_nombre": materia_res.docente_nombre,
            "periodo": {
                "periodo_id": materia_res.periodo.periodo_id,
                "nombre": materia_res.periodo.nombre
            } if materia_res.HasField("periodo") else {}
        }

        # 2. Consultar alumnos en MS-3
        alumnos_res = docentes_alumnos_client.get_alumnos_by_materia(materia_id)
        alumnos = alumnos_res.alumnos if alumnos_res else []

        # 3. Consultar concentrado en MS-4
        concentrado_res = calificaciones_client.get_concentrado(materia_id, modo="actual")
        concentrado_alumnos = concentrado_res.alumnos if concentrado_res else []

        # Generar el archivo
        if formato == "pdf":
            file_bytes = generate_calificaciones_pdf(materia_data, alumnos, concentrado_alumnos)
            content_type = "application/pdf"
            ext = "pdf"
        else:
            file_bytes = generate_calificaciones_excel(materia_data, alumnos, concentrado_alumnos)
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ext = "xlsx"

        filename = f"calificaciones_{materia_data['nrc']}.{ext}"

        # Guardar en base de datos (registro)
        periodo_id = materia_data['periodo'].get('periodo_id') if materia_data.get('periodo') else None
        
        # Validar UUIDs para evitar error de parseo de postgres
        try:
            periodo_uuid = uuid.UUID(periodo_id) if periodo_id else None
            materia_uuid = uuid.UUID(materia_id)
            docente_uuid = uuid.UUID(materia_data['docente_id']) if materia_data.get('docente_id') else None
        except ValueError:
            periodo_uuid = None
            materia_uuid = None
            docente_uuid = None

        registro = {
            "tipo_reporte": "calificaciones",
            "formato": formato.upper(),
            "periodo_id": periodo_uuid,
            "materia_id": materia_uuid,
            "docente_id": docente_uuid,
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(file_bytes),
            "estado": "GENERADO"
        }
        return file_bytes, filename, content_type

    async def generar_reporte_asistencias(self, materia_id: str, formato: str):
        if formato not in ["pdf", "xlsx"]:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use 'pdf' o 'xlsx'.")

        materia_res = periodos_materias_client.get_materia_by_id(materia_id)
        if not materia_res or not materia_res.materia_ofertada_id:
            raise HTTPException(status_code=404, detail="Materia no encontrada en MS-2 (Periodos y Materias).")

        materia_data = {
            "materia_ofertada_id": materia_res.materia_ofertada_id,
            "nrc": materia_res.nrc,
            "seccion": materia_res.seccion,
            "nombre": materia_res.materia.nombre if materia_res.HasField("materia") else "N/A",
            "docente_id": materia_res.docente_id,
            "docente_nombre": materia_res.docente_nombre,
            "periodo": {
                "periodo_id": materia_res.periodo.periodo_id,
                "nombre": materia_res.periodo.nombre
            } if materia_res.HasField("periodo") else {}
        }

        alumnos_res = docentes_alumnos_client.get_alumnos_by_materia(materia_id)
        alumnos = alumnos_res.alumnos if alumnos_res else []

        from app.grpc.clients import asistencias_client
        stats_materia = asistencias_client.get_estadisticas_asistencia(materia_id)
        total_sesiones = stats_materia.total_sesiones_impartidas if stats_materia else 0

        asistencias_data = {}
        for al in alumnos:
            res = asistencias_client.get_asistencia_alumno(al.alumno_id, materia_id)
            if res:
                presentes = res.total_presentes
                retardos = res.total_retardos
            else:
                presentes = 0
                retardos = 0
            
            faltas = total_sesiones - (presentes + retardos) if total_sesiones > 0 else 0
            if faltas < 0: faltas = 0
            
            porcentaje = 0.0
            if total_sesiones > 0:
                porcentaje = ((presentes + retardos) / total_sesiones) * 100.0

            asistencias_data[al.alumno_id] = {
                "presentes": presentes,
                "retardos": retardos,
                "faltas": faltas,
                "porcentaje": porcentaje
            }

        from app.services.pdf_generator import generate_asistencias_pdf
        from app.services.excel_generator import generate_asistencias_excel

        if formato == "pdf":
            file_bytes = generate_asistencias_pdf(materia_data, alumnos, asistencias_data)
            content_type = "application/pdf"
            ext = "pdf"
        else:
            file_bytes = generate_asistencias_excel(materia_data, alumnos, asistencias_data)
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ext = "xlsx"

        filename = f"asistencias_{materia_data['nrc']}.{ext}"

        periodo_id = materia_data['periodo'].get('periodo_id') if materia_data.get('periodo') else None
        try:
            periodo_uuid = uuid.UUID(periodo_id) if periodo_id else None
            materia_uuid = uuid.UUID(materia_id)
            docente_uuid = uuid.UUID(materia_data['docente_id']) if materia_data.get('docente_id') else None
        except ValueError:
            periodo_uuid = None
            materia_uuid = None
            docente_uuid = None

        registro = {
            "tipo_reporte": "asistencias",
            "formato": formato.upper(),
            "periodo_id": periodo_uuid,
            "materia_id": materia_uuid,
            "docente_id": docente_uuid,
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(file_bytes),
            "estado": "GENERADO"
        }
        await self.repository.create(registro)

        return file_bytes, filename, content_type

    def obtener_estadisticas_docente(self, docente_id: str):
        materias_res = periodos_materias_client.get_materias_by_docente(docente_id)
        if not materias_res:
            return {"success": False, "periodos": [], "message": "No se pudieron obtener las materias del docente o no tiene materias."}

        periodos_dict = {}
        from app.grpc.clients import asistencias_client

        for mat in materias_res.materias:
            p_id = mat.periodo.periodo_id if mat.HasField("periodo") else "unknown"
            p_nombre = mat.periodo.nombre if mat.HasField("periodo") else "Desconocido"

            if p_id not in periodos_dict:
                periodos_dict[p_id] = {
                    "periodo_id": p_id,
                    "periodo_nombre": p_nombre,
                    "materias": []
                }

            calif_stats = calificaciones_client.get_estadisticas_materia(mat.materia_ofertada_id)
            asis_stats = asistencias_client.get_estadisticas_asistencia(mat.materia_ofertada_id)

            materia_stats = {
                "periodo_id": p_id,
                "periodo_nombre": p_nombre,
                "materia_id": mat.materia_ofertada_id,
                "materia_nombre": mat.materia.nombre if mat.HasField("materia") else "N/A",
                "nrc": mat.nrc,
                "promedio_grupal": calif_stats.promedio_grupal if calif_stats else 0.0,
                "aprobados": calif_stats.aprobados if calif_stats else 0,
                "reprobados": calif_stats.reprobados if calif_stats else 0,
                "porcentaje_asistencia": asis_stats.porcentaje_asistencia_general if asis_stats else 0.0
            }
            periodos_dict[p_id]["materias"].append(materia_stats)

        return {
            "success": True,
            "periodos": list(periodos_dict.values()),
            "message": "Estadísticas de docente generadas correctamente."
        }

    def obtener_estadisticas_alumno(self, alumno_id: str):
        alumno_res = docentes_alumnos_client.get_alumno_by_id(alumno_id)
        if not alumno_res:
            raise HTTPException(status_code=404, detail="Alumno no encontrado en MS-3.")
        
        return {
            "success": True,
            "alumno": {
                "alumno_id": alumno_res.alumno_id,
                "nombre_completo": alumno_res.nombre_completo,
                "matricula": alumno_res.matricula
            },
            "estadisticas": None,
            "message": "Falta el método gRPC 'GetMateriasByAlumno' en MS-3 para completar este historial. Servicio limitado temporalmente."
        }
