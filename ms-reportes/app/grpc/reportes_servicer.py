import grpc
from app.grpc.generated import reportes_pb2
from app.grpc.generated import reportes_pb2_grpc
from app.db.session import AsyncSessionLocal
from app.repositories.reporte_repository import ReporteRepository
from app.services.reporte_service import ReporteService

class ReportesServicer(reportes_pb2_grpc.ReportesServiceServicer):
    
    async def GenerateReport(self, request, context):
        try:
            async with AsyncSessionLocal() as db:
                repo = ReporteRepository(db)
                service = ReporteService(repo)
                
                if request.tipo == "calificaciones":
                    file_bytes, filename, content_type = await service.generar_reporte_calificaciones(
                        request.materia_id, request.formato
                    )
                elif request.tipo == "asistencias":
                    file_bytes, filename, content_type = await service.generar_reporte_asistencias(
                        request.materia_id, request.formato
                    )
                else:
                    return reportes_pb2.FileBytesResponse(
                        success=False, message="Tipo de reporte desconocido."
                    )
                
                return reportes_pb2.FileBytesResponse(
                    success=True,
                    filename=filename,
                    content_type=content_type,
                    file=file_bytes,
                    message="Reporte generado exitosamente"
                )
        except Exception as e:
            return reportes_pb2.FileBytesResponse(
                success=False,
                message=str(e)
            )

    async def GetHistorialDocente(self, request, context):
        try:
            async with AsyncSessionLocal() as db:
                repo = ReporteRepository(db)
                service = ReporteService(repo)
                
                stats_res = service.obtener_estadisticas_docente(request.docente_id)
                if not stats_res.get("success"):
                    return reportes_pb2.HistorialDocenteResponse(
                        success=False,
                        message=stats_res.get("message", "Error desconocido")
                    )
                
                periodos_proto = []
                for p in stats_res["periodos"]:
                    materias_proto = []
                    for m in p["materias"]:
                        materias_proto.append(reportes_pb2.StatsMateriaPeriodo(
                            periodo_id=m["periodo_id"],
                            periodo_nombre=m["periodo_nombre"],
                            materia_id=m["materia_id"],
                            materia_nombre=m["materia_nombre"],
                            nrc=m["nrc"],
                            promedio_grupal=m["promedio_grupal"],
                            aprobados=m["aprobados"],
                            reprobados=m["reprobados"],
                            porcentaje_asistencia=m["porcentaje_asistencia"]
                        ))
                    
                    periodos_proto.append(reportes_pb2.PeriodoHistorial(
                        periodo_id=p["periodo_id"],
                        periodo_nombre=p["periodo_nombre"],
                        materias=materias_proto
                    ))
                    
                return reportes_pb2.HistorialDocenteResponse(
                    success=True,
                    periodos=periodos_proto,
                    message=stats_res["message"]
                )
        except Exception as e:
            return reportes_pb2.HistorialDocenteResponse(
                success=False,
                message=str(e)
            )
