from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ResultadoValidacionQr
from app.models.token_qr_usado import TokenQrUsado


class RepositorioTokens:
    """
    Repositorio para gestionar las operaciones de base de datos
    relacionadas con la entidad TokenQrUsado (Seguridad Anti-Replay).
    """

    @staticmethod
    async def registrar_token_qr_usado(
        db: AsyncSession,
        id_sesion: int,
        id_alumno: int,
        identificador_unico_qr: str,
        huella_token: str,
        fecha_hora_emision: datetime,
        fecha_hora_expiracion: datetime,
        resultado_validacion: ResultadoValidacionQr,
        motivo_rechazo: str | None = None,
    ) -> TokenQrUsado:
        """
        Guarda el registro de que un token QR específico fue procesado.
        """
        nuevo_token = TokenQrUsado(
            id_sesion=id_sesion,
            id_alumno=id_alumno,
            identificador_unico_qr=identificador_unico_qr,
            huella_token=huella_token,
            fecha_hora_emision=fecha_hora_emision,
            fecha_hora_expiracion=fecha_hora_expiracion,
            fecha_hora_uso=datetime.utcnow(),
            resultado_validacion=resultado_validacion,
            motivo_rechazo=motivo_rechazo,
        )
        db.add(nuevo_token)
        await db.flush()
        await db.refresh(nuevo_token)
        return nuevo_token

    @staticmethod
    async def existe_identificador_unico_qr(db: AsyncSession, identificador_unico_qr: str) -> bool:
        """
        Verifica si un identificador de QR ya fue escaneado antes (evita reutilización).
        """
        query = select(TokenQrUsado).where(
            TokenQrUsado.identificador_unico_qr == identificador_unico_qr
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def existe_huella_token(db: AsyncSession, huella_token: str) -> bool:
        """
        Verifica si el hash completo de un token ya fue utilizado.
        """
        query = select(TokenQrUsado).where(TokenQrUsado.huella_token == huella_token)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
