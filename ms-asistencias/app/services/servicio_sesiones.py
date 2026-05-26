from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.messaging.clients.periodos_hybrid_client import periodos_client
from app.models.enums import EstadoSesion
from app.models.sesion_asistencia import SesionAsistencia
from app.repositories.repositorio_sesiones import RepositorioSesiones


class ServicioSesiones:
    """
    Contiene toda la lógica de negocio para gestionar el ciclo de vida
    de las sesiones de asistencia.
    """

    @staticmethod
    async def iniciar_sesion(
        db: AsyncSession, id_materia: str, id_docente: str
    ) -> SesionAsistencia:
        """
        Inicia una nueva sesión de asistencia.
        """
        # --- FASE 11: Integración gRPC con MS-2 (Materias) ---
        # Verificamos si la materia existe y le pertenece al docente.
        es_valido = await periodos_client.verificar_materia_docente(id_materia, id_docente)
        if not es_valido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El docente no tiene asignada esta materia o la materia no existe."
            )
        # ------------------------------------------------------

        # 1. Validar que la materia no tenga ya una sesión activa
        sesion_existente = await RepositorioSesiones.obtener_sesion_activa_por_materia(
            db=db, id_materia=id_materia
        )
        if sesion_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una sesión activa para esta materia.",
            )

        # 2. Calcular los tiempos de la sesión usando la configuración global
        ahora = datetime.now(timezone.utc)
        limite_presente = ahora + timedelta(minutes=settings.PRESENT_LIMIT_MINUTES)
        limite_fin = ahora + timedelta(minutes=settings.SESSION_DURATION_MINUTES)

        # 3. Crear la sesión en la base de datos
        nueva_sesion = await RepositorioSesiones.crear_sesion(
            db=db,
            id_materia=id_materia,
            id_docente=id_docente,
            fecha_hora_inicio=ahora,
            fecha_hora_limite_presente=limite_presente,
            fecha_hora_fin=limite_fin,
        )

        # TODO: En un futuro aquí se podría emitir un evento para WebSocket
        # o registrar la sesión en Redis para mayor velocidad.

        return nueva_sesion

    @staticmethod
    async def obtener_sesion(db: AsyncSession, id_sesion: int) -> SesionAsistencia:
        """
        Obtiene los detalles de una sesión específica.
        """
        sesion = await RepositorioSesiones.obtener_sesion_por_id(db, id_sesion)
        if not sesion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La sesión especificada no existe.",
            )
        return sesion

    @staticmethod
    async def cerrar_sesion(db: AsyncSession, id_sesion: int) -> dict:
        """
        Cierra una sesión de forma manual (por parte del docente) y registra ausencias.
        """
        # 1. Validar que la sesión exista
        sesion = await RepositorioSesiones.obtener_sesion_por_id(db=db, id_sesion=id_sesion)
        if not sesion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La sesión especificada no existe.",
            )

        # 2. Validar que no esté ya cerrada o expirada
        if sesion.estado_sesion != EstadoSesion.ACTIVA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La sesión ya está {sesion.estado_sesion.value}.",
            )

        # 3. Consultar alumnos en MS-3 antes de cerrar
        from app.grpc_clients.cliente_alumnos import cliente_alumnos
        from app.repositories.repositorio_asistencias import RepositorioAsistencias
        from app.models.enums import EstadoAsistencia, MetodoRegistro
        import logging

        try:
            # Obtener los alumnos inscritos en la materia desde MS-3
            alumnos_inscritos = await cliente_alumnos.obtener_alumnos_por_materia(sesion.id_materia)
        except Exception as e:
            logging.error(f"Error al obtener alumnos inscritos de MS-3 para sesión {id_sesion}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo consultar la lista de alumnos para registrar ausencias. La sesión no fue cerrada."
            )

        # 4. Cerrar la sesión
        ahora = datetime.now(timezone.utc)
        actualizado = await RepositorioSesiones.cerrar_sesion(
            db=db, id_sesion=id_sesion, fecha_hora_cierre=ahora
        )

        if not actualizado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocurrió un error al intentar cerrar la sesión.",
            )

        # 5. Registrar ausentes
        try:
            # Obtener las asistencias ya registradas (Presente, Retardo) para esta sesión
            asistencias_existentes = await RepositorioAsistencias.listar_asistencias_por_sesion(db, id_sesion)
            ids_alumnos_asistieron = {a.id_alumno for a in asistencias_existentes}

            for alumno in alumnos_inscritos:
                id_alumno = alumno["id_alumno"]
                if id_alumno not in ids_alumnos_asistieron:
                    # Guardamos al alumno ausente
                    await RepositorioAsistencias.crear_registro_asistencia(
                        db=db,
                        id_sesion=id_sesion,
                        id_alumno=id_alumno,
                        matricula=alumno["matricula"],
                        estado_asistencia=EstadoAsistencia.AUSENTE,
                        metodo_registro=MetodoRegistro.SISTEMA,
                        observaciones="Registrado automáticamente por el sistema al cerrar la sesión de asistencia."
                    )
        except Exception as e:
            logging.error(f"Error registrando ausencias automáticas para sesión {id_sesion}: {str(e)}")

        return {"mensaje": "Sesión cerrada exitosamente", "id_sesion": id_sesion}

    @staticmethod
    async def verificar_y_marcar_expiradas(db: AsyncSession, id_sesion: int):
        """
        Este método podría ser llamado por un cronjob o en el endpoint de validación
        para marcar sesiones que ya superaron sus 10 minutos y el docente no las cerró.
        """
        sesion = await RepositorioSesiones.obtener_sesion_por_id(db=db, id_sesion=id_sesion)
        if sesion and sesion.estado_sesion == EstadoSesion.ACTIVA:
            fecha_hora_fin = sesion.fecha_hora_fin
            if fecha_hora_fin.tzinfo is None:
                fecha_hora_fin = fecha_hora_fin.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > fecha_hora_fin:
                await RepositorioSesiones.marcar_sesion_expirada(db=db, id_sesion=id_sesion)
