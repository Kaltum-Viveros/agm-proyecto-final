import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.repositories.repositorio_sesiones import RepositorioSesiones
from app.models.enums import EstadoSesion
from app.grpc_clients.cliente_alumnos import cliente_alumnos


class ServicioQr:
    """
    Contiene la lógica de negocio para la generación, cifrado,
    descifrado y validación de los tokens QR dinámicos.
    """

    # Instancia de Fernet con la clave secreta de las variables de entorno
    _fernet = Fernet(settings.QR_SECRET_KEY.encode("utf-8"))

    @staticmethod
    async def generar_token_qr(db: AsyncSession, id_sesion: int, id_alumno: str, matricula: str) -> dict:
        """
        Genera un token QR cifrado con un tiempo de vida corto (ej. 20 segundos).
        Retorna un diccionario con el token cifrado y su fecha límite.
        """
        # 1. Buscar la sesión local por id_sesion
        sesion = await RepositorioSesiones.obtener_sesion_por_id(db=db, id_sesion=id_sesion)
        if not sesion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La sesión de asistencia especificada no existe.",
            )

        # 2. Validar que la sesión esté ACTIVA y no expirada
        if sesion.estado_sesion != EstadoSesion.ACTIVA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La sesión ya no está activa. Estado actual: {sesion.estado_sesion.value}.",
            )

        ahora = datetime.now(timezone.utc)
        fecha_hora_fin = sesion.fecha_hora_fin
        if fecha_hora_fin.tzinfo is None:
            fecha_hora_fin = fecha_hora_fin.replace(tzinfo=timezone.utc)
        if ahora > fecha_hora_fin:
            # Marcar como expirada por si acaso
            await RepositorioSesiones.marcar_sesion_expirada(db=db, id_sesion=id_sesion)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La sesión de asistencia ha expirado.",
            )

        # 3. Validar alumno-materia con MS-3 (Alumnos) a través de gRPC
        id_materia = sesion.id_materia
        inscrito = await cliente_alumnos.verificar_alumno_en_materia(id_alumno, id_materia)
        if not inscrito:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El alumno no está inscrito en la materia asignada a esta sesión.",
            )

        expiracion = ahora + timedelta(seconds=settings.QR_TTL_SECONDS)

        # Generar un identificador único (nonce) para evitar ataques de repetición
        identificador_unico = str(uuid.uuid4())

        payload = {
            "id_sesion": id_sesion,
            "id_alumno": id_alumno,
            "matricula": matricula,
            "uuid": identificador_unico,
            "emision": ahora.isoformat(),
            "expiracion": expiracion.isoformat(),
        }

        # Convertir a JSON y cifrar
        payload_bytes = json.dumps(payload).encode("utf-8")
        token_cifrado = ServicioQr._fernet.encrypt(payload_bytes).decode("utf-8")

        return {
            "token": token_cifrado,
            "expiracion": expiracion.isoformat(),
            "tiempo_vida_segundos": settings.QR_TTL_SECONDS,
        }

    @staticmethod
    def descifrar_y_validar_token(token_cifrado: str) -> dict:
        """
        Descifra el token QR. Si es inválido, está corrupto o ya expiró, lanza un HTTPException.
        """
        try:
            # Descifrar
            payload_bytes = ServicioQr._fernet.decrypt(token_cifrado.encode("utf-8"))
            payload = json.loads(payload_bytes.decode("utf-8"))

            # Validar expiración (El TTL que viene dentro del token)
            expiracion = datetime.fromisoformat(payload["expiracion"])
            if expiracion.tzinfo is None:
                expiracion = expiracion.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expiracion:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El token QR ha expirado. Por favor, genere uno nuevo.",
                )

            return payload

        except InvalidToken:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token QR inválido o corrupto.",
            )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de token QR no reconocido.",
            )
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token QR incompleto. Falta el campo: {str(e)}",
            )

    @staticmethod
    def generar_huella_token(token_cifrado: str) -> str:
        """
        Genera un hash SHA-256 del token cifrado completo.
        Se usa para guardar el registro en la BD sin almacenar el token original.
        """
        return hashlib.sha256(token_cifrado.encode("utf-8")).hexdigest()
