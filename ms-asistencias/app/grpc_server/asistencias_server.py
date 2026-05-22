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
            from app.grpc_clients.cliente_alumnos import cliente_alumnos
            
            # Obtener sesiones de la materia
            query_sesiones = select(SesionAsistencia).where(
                SesionAsistencia.id_materia == request.id_materia
            )
            result_sesiones = await db.execute(query_sesiones)
            sesiones = result_sesiones.scalars().all()
            total_sesiones = len(sesiones)

            if total_sesiones == 0:
                return asistencias_pb2.EstadisticasResponse(
                    total_alumnos=0,
                    porcentaje_asistencia_general=0.0,
                    total_sesiones_impartidas=0,
                )

            # Obtener alumnos inscritos desde MS-3
            try:
                alumnos_inscritos = await cliente_alumnos.obtener_alumnos_por_materia(request.id_materia)
                total_alumnos = len(alumnos_inscritos)
            except Exception as e:
                import logging
                logging.error(f"Error MS-3 en GetEstadisticasAsistencia: {str(e)}")
                context.abort(grpc.StatusCode.UNAVAILABLE, "No se pudo consultar el total de alumnos.")
                return asistencias_pb2.EstadisticasResponse()

            # Obtener todos los registros de esas sesiones
            ids_sesiones = [s.id_sesion for s in sesiones]
            query_registros = select(RegistroAsistencia).where(
                RegistroAsistencia.id_sesion.in_(ids_sesiones)
            )
            result_registros = await db.execute(query_registros)
            registros = result_registros.scalars().all()

            presentes = sum(1 for r in registros if r.estado_asistencia == EstadoAsistencia.PRESENTE)
            retardos = sum(1 for r in registros if r.estado_asistencia == EstadoAsistencia.RETARDO)
            
            total_posibles_asistencias = total_alumnos * total_sesiones
            asistencias_validas = presentes + retardos
            
            porcentaje_asistencia_general = 0.0
            if total_posibles_asistencias > 0:
                porcentaje_asistencia_general = (asistencias_validas / total_posibles_asistencias) * 100.0

            return asistencias_pb2.EstadisticasResponse(
                total_alumnos=total_alumnos,
                porcentaje_asistencia_general=round(porcentaje_asistencia_general, 2),
                total_sesiones_impartidas=total_sesiones,
            )


async def serve():
    """
    Levanta el servidor gRPC de manera asíncrona en el puerto 50055.
    """
    server = grpc.aio.server()
    asistencias_pb2_grpc.add_AsistenciasServiceServicer_to_server(AsistenciasServicer(), server)
    # NOTA DE SEGURIDAD: add_insecure_port se utiliza únicamente para comunicación interna
    # dentro de la red confiable de Docker/desarrollo.
    # En producción real (sobre redes públicas), se debe implementar mTLS/TLS.
    server.add_insecure_port("[::]:50055")
    print("Servidor gRPC Asistencias iniciado en el puerto 50055...")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())
