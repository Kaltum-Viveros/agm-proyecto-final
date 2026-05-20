from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import EstadoSesion
from app.models.sesion_asistencia import SesionAsistencia


class RepositorioSesiones:
    """
    Repositorio para gestionar las operaciones de base de datos
    relacionadas con la entidad SesionAsistencia.
    """

    @staticmethod
    async def crear_sesion(
        db: AsyncSession,
        id_materia: str,
        id_docente: str,
        fecha_hora_inicio: datetime,
        fecha_hora_limite_presente: datetime,
        fecha_hora_fin: datetime,
    ) -> SesionAsistencia:
        """
        Crea una nueva sesión de asistencia en la base de datos y la retorna.
        Por defecto, el estado será ACTIVA.
        """
        nueva_sesion = SesionAsistencia(
            id_materia=id_materia,
            id_docente=id_docente,
            fecha_hora_inicio=fecha_hora_inicio,
            fecha_hora_limite_presente=fecha_hora_limite_presente,
            fecha_hora_fin=fecha_hora_fin,
            estado_sesion=EstadoSesion.ACTIVA,
        )
        db.add(nueva_sesion)
        await db.flush()  # Para obtener el id_sesion generado sin hacer commit todavía
        await db.refresh(nueva_sesion)
        return nueva_sesion

    @staticmethod
    async def obtener_sesion_por_id(db: AsyncSession, id_sesion: int) -> SesionAsistencia | None:
        """
        Busca una sesión específica por su ID.
        """
        query = select(SesionAsistencia).where(SesionAsistencia.id_sesion == id_sesion)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def obtener_sesion_activa_por_materia(db: AsyncSession, id_materia: str) -> SesionAsistencia | None:
        """
        Devuelve la sesión que se encuentre en estado ACTIVA para una materia específica.
        Si no hay ninguna, retorna None.
        """
        query = select(SesionAsistencia).where(
            SesionAsistencia.id_materia == id_materia,
            SesionAsistencia.estado_sesion == EstadoSesion.ACTIVA,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def cerrar_sesion(db: AsyncSession, id_sesion: int, fecha_hora_cierre: datetime) -> bool:
        """
        Cambia el estado de una sesión a CERRADA y registra la fecha de cierre.
        Retorna True si la actualización fue exitosa.
        """
        query = (
            update(SesionAsistencia)
            .where(SesionAsistencia.id_sesion == id_sesion)
            .values(
                estado_sesion=EstadoSesion.CERRADA,
                fecha_hora_cierre=fecha_hora_cierre,
            )
        )
        result = await db.execute(query)
        return result.rowcount > 0

    @staticmethod
    async def marcar_sesion_expirada(db: AsyncSession, id_sesion: int) -> bool:
        """
        Cambia el estado de una sesión a EXPIRADA (cuando el tiempo se agota sin que el docente la cierre manualmente).
        """
        query = (
            update(SesionAsistencia)
            .where(SesionAsistencia.id_sesion == id_sesion)
            .values(estado_sesion=EstadoSesion.EXPIRADA)
        )
        result = await db.execute(query)
        return result.rowcount > 0

    @staticmethod
    async def listar_sesiones_de_hoy_por_materia(db: AsyncSession, id_materia: str) -> list[SesionAsistencia]:
        """
        Devuelve las sesiones de una materia creadas en el día actual (UTC).
        """
        hoy = datetime.now(timezone.utc).date()
        inicio_dia = datetime(hoy.year, hoy.month, hoy.day, tzinfo=timezone.utc)
        fin_dia = datetime(hoy.year, hoy.month, hoy.day, 23, 59, 59, 999999, tzinfo=timezone.utc)
        
        query = select(SesionAsistencia).where(
            SesionAsistencia.id_materia == id_materia,
            SesionAsistencia.fecha_hora_inicio >= inicio_dia,
            SesionAsistencia.fecha_hora_inicio <= fin_dia
        )
        result = await db.execute(query)
        return list(result.scalars().all())

