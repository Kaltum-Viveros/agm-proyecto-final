import grpc
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.generated import asistencias_pb2, asistencias_pb2_grpc
from app.models.enums import EstadoAsistencia
from app.models.registro_asistencia import RegistroAsistencia
from app.models.sesion_asistencia import SesionAsistencia


class AsistenciasServicer(asistencias_pb2_grpc.AsistenciasServiceServicer):
    """
    Implementación del servidor gRPC para MS-5.
    Permite que otros microservicios (ej. Calificaciones o Reportes)
    obtengan datos de asistencias de forma directa y ultrarrápida.
    """

    async def GetAsistenciaAlumno(self, request, context):
        """
        Devuelve el historial de un alumno en una materia.
        """
        async with AsyncSessionLocal() as db:
            query = (
                select(RegistroAsistencia)
                .join(SesionAsistencia, RegistroAsistencia.id_sesion == SesionAsistencia.id_sesion)
                .where(
                    RegistroAsistencia.id_alumno == request.id_alumno,
                    SesionAsistencia.id_materia == request.id_materia,
                )
            )
            resultado = await db.execute(query)
            registros = resultado.scalars().all()

            # Clasificar y contar
            detalles = []
            presentes = 0
            retardos = 0

            for reg in registros:
                if reg.estado_asistencia == EstadoAsistencia.PRESENTE:
                    presentes += 1
                elif reg.estado_asistencia == EstadoAsistencia.RETARDO:
                    retardos += 1

                detalles.append(
                    asistencias_pb2.DetalleAsistenciaProto(
                        id_sesion=reg.id_sesion,
                        estado=reg.estado_asistencia.name,
                        fecha_registro=reg.fecha_hora_registro.isoformat(),
                    )
                )

            return asistencias_pb2.AsistenciaAlumnoResponse(
                asistencias=detalles,
                total_presentes=presentes,
                total_retardos=retardos,
            )

    async def GetAsistenciasMateria(self, request, context):
        """
        Devuelve el conteo de asistencias de todos los alumnos de una materia de golpe (Solución N+1).
        """
        async with AsyncSessionLocal() as db:
            query = (
                select(RegistroAsistencia)
                .join(SesionAsistencia, RegistroAsistencia.id_sesion == SesionAsistencia.id_sesion)
                .where(SesionAsistencia.id_materia == request.id_materia)
            )
            resultado = await db.execute(query)
            registros = resultado.scalars().all()

            # Agrupar por id_alumno
            resumen_alumnos = {}
            for reg in registros:
                if reg.id_alumno not in resumen_alumnos:
                    resumen_alumnos[reg.id_alumno] = {"presentes": 0, "retardos": 0}
                
                if reg.estado_asistencia == EstadoAsistencia.PRESENTE:
                    resumen_alumnos[reg.id_alumno]["presentes"] += 1
                elif reg.estado_asistencia == EstadoAsistencia.RETARDO:
                    resumen_alumnos[reg.id_alumno]["retardos"] += 1

            # Formatear a Proto
            lista_asistencias = []
            for alumno_id, data in resumen_alumnos.items():
                lista_asistencias.append(asistencias_pb2.ResumenAsistenciaAlumno(
                    id_alumno=alumno_id,
                    total_presentes=data["presentes"],
                    total_retardos=data["retardos"]
                ))

            return asistencias_pb2.AsistenciasMateriaResponse(
                asistencias=lista_asistencias
            )

    async def GetEstadisticasAsistencia(self, request, context):
        """
        Calcula un resumen estadístico de la materia para el Dashboard del docente.
        """
        async with AsyncSessionLocal() as db:
            # Lógica simplificada
            query_sesiones = select(SesionAsistencia).where(
                SesionAsistencia.id_materia == request.id_materia
            )
            result_sesiones = await db.execute(query_sesiones)
            total_sesiones = len(result_sesiones.scalars().all())

            return asistencias_pb2.EstadisticasResponse(
                total_alumnos=0,  # Dependería de MS-3 (Alumnos) 
                porcentaje_asistencia_general=100.0 if total_sesiones > 0 else 0.0,
                total_sesiones_impartidas=total_sesiones,
            )


async def serve():
    """
    Levanta el servidor gRPC de manera asíncrona en el puerto 50055.
    """
    server = grpc.aio.server()
    asistencias_pb2_grpc.add_AsistenciasServiceServicer_to_server(AsistenciasServicer(), server)
    server.add_insecure_port("[::]:50055")
    print("Servidor gRPC Asistencias iniciado en el puerto 50055...")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())
