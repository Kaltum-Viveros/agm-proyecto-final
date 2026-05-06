import hashlib
import json
import uuid
from datetime import datetime, timedelta

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status

from app.core.config import settings


class ServicioQr:
    """
    Contiene la lógica de negocio para la generación, cifrado,
    descifrado y validación de los tokens QR dinámicos.
    """

    # Instancia de Fernet con la clave secreta de las variables de entorno
    _fernet = Fernet(settings.QR_SECRET_KEY.encode("utf-8"))

    @staticmethod
    def generar_token_qr(id_sesion: int, id_alumno: int, matricula: str) -> dict:
        """
        Genera un token QR cifrado con un tiempo de vida corto (ej. 20 segundos).
        Retorna un diccionario con el token cifrado y su fecha límite.
        """
        ahora = datetime.utcnow()
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
            if datetime.utcnow() > expiracion:
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
