from datetime import date, datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import EstadoAsistencia, MetodoRegistro
from app.models.registro_asistencia import RegistroAsistencia


class RepositorioAsistencias:
    """
    Repositorio para gestionar las operaciones de base de datos
    relacionadas con la entidad RegistroAsistencia.
    """

    @staticmethod
    async def crear_registro_asistencia(
        db: AsyncSession,
        id_sesion: int,
        id_alumno: str,
        matricula: str,
        estado_asistencia: EstadoAsistencia,
        identificador_qr: str | None = None,
        fecha_hora_emision_qr: datetime | None = None,
        metodo_registro: MetodoRegistro = MetodoRegistro.QR,
        observaciones: str | None = None,
    ) -> RegistroAsistencia:
        """
        Guarda un nuevo registro de asistencia de un alumno para una sesión.
        """
        nuevo_registro = RegistroAsistencia(
            id_sesion=id_sesion,
            id_alumno=id_alumno,
            matricula=matricula,
            estado_asistencia=estado_asistencia,
            identificador_qr=identificador_qr,
            fecha_hora_emision_qr=fecha_hora_emision_qr,
            metodo_registro=metodo_registro,
            observaciones=observaciones,
        )
        db.add(nuevo_registro)
        await db.flush()
        await db.refresh(nuevo_registro)
        return nuevo_registro

    @staticmethod
    async def obtener_registro_por_sesion_y_alumno(
        db: AsyncSession, id_sesion: int, id_alumno: str
    ) -> RegistroAsistencia | None:
        """
        Verifica si un alumno ya tiene un registro de asistencia en una sesión específica.
        """
        query = select(RegistroAsistencia).where(
            RegistroAsistencia.id_sesion == id_sesion,
            RegistroAsistencia.id_alumno == id_alumno,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def listar_asistencias_por_sesion(db: AsyncSession, id_sesion: int) -> Sequence[RegistroAsistencia]:
        """
        Devuelve todos los registros de asistencia de una sesión.
        """
        query = select(RegistroAsistencia).where(RegistroAsistencia.id_sesion == id_sesion)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def listar_asistencias_por_lista_sesiones(db: AsyncSession, ids_sesiones: list[int]) -> Sequence[RegistroAsistencia]:
        """
        Devuelve los registros de asistencia para una lista de IDs de sesión.
        """
        if not ids_sesiones:
            return []
        query = select(RegistroAsistencia).where(RegistroAsistencia.id_sesion.in_(ids_sesiones))
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def obtener_estadisticas_por_sesion(db: AsyncSession, id_sesion: int) -> dict:
        """
        Obtiene el conteo base de estados de asistencia en una sesión.
        """
        query = select(RegistroAsistencia.estado_asistencia).where(RegistroAsistencia.id_sesion == id_sesion)
        result = await db.execute(query)
        estados = result.scalars().all()
        
        presentes = sum(1 for e in estados if e == EstadoAsistencia.PRESENTE)
        retardos = sum(1 for e in estados if e == EstadoAsistencia.RETARDO)
        ausentes = sum(1 for e in estados if e == EstadoAsistencia.AUSENTE)
        
        return {
            "presentes": presentes,
            "retardos": retardos,
            "ausentes_registrados": ausentes, # Estos son los que se marcaron manualmente como ausentes
            "total_registrados": len(estados)
        }

