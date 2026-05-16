from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.grpc_clients.cliente_materias import cliente_materias
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
        db: AsyncSession, id_materia: int, id_docente: int
    ) -> SesionAsistencia:
        """
        Inicia una nueva sesión de asistencia.
        """
        # --- FASE 11: Integración gRPC con MS-2 (Materias) ---
        # Verificamos si la materia existe y le pertenece al docente.
        # Descomenta las siguientes líneas cuando MS-2 esté en ejecución.
        # es_valido = await cliente_materias.verificar_materia_docente(id_materia, id_docente)
        # if not es_valido:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="La materia no existe o no tienes permiso para abrir una sesión aquí."
        #     )
        # ------------------------------------------------------

        # 1. Validar que la materia no tenga ya una sesión activa
        sesion_existente = await RepositorioSesiones.obtener_sesion_activa_por_materia(
            db=db, id_materia=id_materia
        )
        if sesion_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una sesión activa para esta materia.",
            )

        # 2. Calcular los tiempos de la sesión usando la configuración global
        ahora = datetime.utcnow()
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
    async def cerrar_sesion(db: AsyncSession, id_sesion: int) -> dict:
        """
        Cierra una sesión de forma manual (por parte del docente).
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

        # 3. Cerrar la sesión
        ahora = datetime.utcnow()
        actualizado = await RepositorioSesiones.cerrar_sesion(
            db=db, id_sesion=id_sesion, fecha_hora_cierre=ahora
        )

        if not actualizado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocurrió un error al intentar cerrar la sesión.",
            )

        return {"mensaje": "Sesión cerrada exitosamente", "id_sesion": id_sesion}

    @staticmethod
    async def verificar_y_marcar_expiradas(db: AsyncSession, id_sesion: int):
        """
        Este método podría ser llamado por un cronjob o en el endpoint de validación
        para marcar sesiones que ya superaron sus 10 minutos y el docente no las cerró.
        """
        sesion = await RepositorioSesiones.obtener_sesion_por_id(db=db, id_sesion=id_sesion)
        if sesion and sesion.estado_sesion == EstadoSesion.ACTIVA:
            if datetime.utcnow() > sesion.fecha_hora_fin:
                await RepositorioSesiones.marcar_sesion_expirada(db=db, id_sesion=id_sesion)
