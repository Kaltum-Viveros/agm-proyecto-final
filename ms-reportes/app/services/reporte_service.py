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
        await self.repository.create(registro)

        return file_bytes, filename, content_type
