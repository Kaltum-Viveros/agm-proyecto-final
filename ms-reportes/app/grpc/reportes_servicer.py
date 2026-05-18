import grpc
from app.grpc.generated import reportes_pb2, reportes_pb2_grpc

class ReportesServicer(reportes_pb2_grpc.ReportesServiceServicer):
    
    def GenerateReport(self, request, context):
        # TODO: Implementar lógica de generación de reportes
        return reportes_pb2.FileBytesResponse(
            success=True,
            filename=f"reporte_{request.tipo}.txt",
            content_type="text/plain",
            file=b"Contenido del reporte de prueba",
            message="Reporte generado exitosamente (Mock temporal)"
        )

    def GetHistorialDocente(self, request, context):
        # TODO: Implementar la consulta real de estadísticas e historial
        return reportes_pb2.HistorialDocenteResponse(
            success=True,
            periodos=[],
            message="Historial obtenido exitosamente (Mock temporal)"
        )
