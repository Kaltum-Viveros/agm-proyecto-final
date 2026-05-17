from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import EstadoAsistencia, EstadoSesion, ResultadoValidacionQr
from app.grpc_clients.cliente_alumnos import cliente_alumnos
from app.repositories.repositorio_asistencias import RepositorioAsistencias
from app.repositories.repositorio_sesiones import RepositorioSesiones
from app.repositories.repositorio_tokens import RepositorioTokens
from app.services.servicio_qr import ServicioQr


class ServicioAsistencias:
    """
    Contiene la lógica de negocio principal para procesar un pase de lista:
    valida el QR, previene duplicados, clasifica retardo/presente y guarda todo.
    """

    @staticmethod
    async def registrar_asistencia(db: AsyncSession, token_cifrado: str) -> dict:
        """
        Flujo completo para procesar un QR escaneado por el docente.
        """
        ahora = datetime.utcnow()
        huella = ServicioQr.generar_huella_token(token_cifrado)

        # 1. Validar que el hash del token exacto no se haya usado antes (seguridad extrema)
        if await RepositorioTokens.existe_huella_token(db, huella):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este código QR ya fue escaneado anteriormente.",
            )

        # 2. Descifrar y validar el tiempo de vida interno del QR
        payload = ServicioQr.descifrar_y_validar_token(token_cifrado)
        id_sesion = payload["id_sesion"]
        id_alumno = payload["id_alumno"]
        matricula = payload["matricula"]
        uuid_qr = payload["uuid"]
        fecha_emision_qr = datetime.fromisoformat(payload["emision"])
        fecha_expiracion_qr = datetime.fromisoformat(payload["expiracion"])

        # 3. Validar que el UUID no se haya usado en otro token modificado
        if await RepositorioTokens.existe_identificador_unico_qr(db, uuid_qr):
            # Intentaron hacer trampa regerando el token con la misma firma interna
            await ServicioAsistencias._registrar_auditoria_qr(
                db, id_sesion, id_alumno, uuid_qr, huella, fecha_emision_qr, fecha_expiracion_qr, ResultadoValidacionQr.DUPLICADO, "UUID reutilizado"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="QR clonado o reutilizado.",
            )

        # 4. Validar que la sesión exista y siga abierta
        sesion = await RepositorioSesiones.obtener_sesion_por_id(db, id_sesion)
        if not sesion or sesion.estado_sesion != EstadoSesion.ACTIVA:
            await ServicioAsistencias._registrar_auditoria_qr(
                db, id_sesion, id_alumno, uuid_qr, huella, fecha_emision_qr, fecha_expiracion_qr, ResultadoValidacionQr.RECHAZADO, "Sesión no activa"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La sesión de asistencia no está activa o ya expiró.",
            )

        # --- FASE 11: Integración gRPC con MS-3 (Alumnos) ---
        # Verificamos si el alumno está realmente inscrito en esta materia.
        # Descomenta las siguientes líneas cuando MS-3 esté en ejecución.
        # id_materia = sesion.id_materia
        # esta_inscrito = await cliente_alumnos.verificar_alumno_en_materia(id_alumno, id_materia)
        # if not esta_inscrito:
        #     await ServicioAsistencias._registrar_auditoria_qr(
        #         db, id_sesion, id_alumno, uuid_qr, huella, fecha_emision_qr, fecha_expiracion_qr, ResultadoValidacionQr.RECHAZADO, "No inscrito en la materia"
        #     )
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="El alumno no está inscrito en esta materia.",
        #     )
        # ------------------------------------------------------

        # 5. Validar que el alumno no haya pasado lista ya en esta misma sesión
        registro_previo = await RepositorioAsistencias.obtener_registro_por_sesion_y_alumno(db, id_sesion, id_alumno)
        if registro_previo:
            await ServicioAsistencias._registrar_auditoria_qr(
                db, id_sesion, id_alumno, uuid_qr, huella, fecha_emision_qr, fecha_expiracion_qr, ResultadoValidacionQr.DUPLICADO, "Asistencia ya registrada"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El alumno ya tiene registrada su asistencia en esta sesión.",
            )

        # 6. Clasificar PRESENTE o RETARDO
        # Si la fecha actual es menor o igual al límite marcado por la sesión
        estado_asistencia = EstadoAsistencia.PRESENTE
        if ahora > sesion.fecha_hora_limite_presente:
            estado_asistencia = EstadoAsistencia.RETARDO

        # 7. Todo bien: Guardar el pase de lista
        registro = await RepositorioAsistencias.crear_registro_asistencia(
            db=db,
            id_sesion=id_sesion,
            id_alumno=id_alumno,
            matricula=matricula,
            estado_asistencia=estado_asistencia,
            identificador_qr=uuid_qr,
            fecha_hora_emision_qr=fecha_emision_qr,
        )

        # 8. Guardar la huella del token en auditoría como ACEPTADO
        await ServicioAsistencias._registrar_auditoria_qr(
            db, id_sesion, id_alumno, uuid_qr, huella, fecha_emision_qr, fecha_expiracion_qr, ResultadoValidacionQr.ACEPTADO
        )

        return {
            "mensaje": f"Asistencia registrada como {estado_asistencia.value}",
            "estado": estado_asistencia.value,
            "id_asistencia": registro.id_asistencia
        }

    @staticmethod
    async def _registrar_auditoria_qr(
        db: AsyncSession, id_sesion: int, id_alumno: int, uuid_qr: str, huella: str, emision: datetime, expiracion: datetime, resultado: ResultadoValidacionQr, motivo: str | None = None
    ):
        """
        Helper privado para dejar el rastro del token en la tabla tokens_qr_usados.
        """
        await RepositorioTokens.registrar_token_qr_usado(
            db=db,
            id_sesion=id_sesion,
            id_alumno=id_alumno,
            identificador_unico_qr=uuid_qr,
            huella_token=huella,
            fecha_hora_emision=emision,
            fecha_hora_expiracion=expiracion,
            resultado_validacion=resultado,
            motivo_rechazo=motivo
        )

    @staticmethod
    async def obtener_estadisticas_sesion(db: AsyncSession, id_sesion: int) -> dict:
        """
        Calcula las estadísticas de asistencia de una sesión.
        """
        # 1. Validar que la sesión exista
        sesion = await RepositorioSesiones.obtener_sesion_por_id(db, id_sesion)
        if not sesion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La sesión especificada no existe.",
            )

        # 2. Obtener conteos básicos
        stats = await RepositorioAsistencias.obtener_estadisticas_por_sesion(db, id_sesion)
        
        # --- FASE 11: Integración gRPC con MS-3 (Alumnos) ---
        # Idealmente, consultamos MS-3 para saber el total de alumnos inscritos.
        # Por ahora lo simulamos ya que MS-3 podría no estar activo en local.
        # total_alumnos = await cliente_alumnos.obtener_total_alumnos_materia(sesion.id_materia)
        total_alumnos = 40  # MOCK para pruebas locales
        # ------------------------------------------------------
        
        # 3. Calcular ausentes y porcentaje (asumiendo que los que no pasaron lista están ausentes)
        ausentes_reales = stats["ausentes_registrados"] + max(0, total_alumnos - stats["total_registrados"])
        total_presentes_retardos = stats["presentes"] + stats["retardos"]
        
        porcentaje = 0.0
        if total_alumnos > 0:
            porcentaje = round((total_presentes_retardos / total_alumnos) * 100, 2)
            
        return {
            "total_alumnos": total_alumnos,
            "presentes": stats["presentes"],
            "retardos": stats["retardos"],
            "ausentes": ausentes_reales,
            "porcentaje_asistencia": porcentaje
        }

    @staticmethod
    async def obtener_asistencias_hoy_materia(db: AsyncSession, id_materia: int) -> list:
        """
        Obtiene los registros de asistencia de todas las sesiones de la materia en el día actual.
        """
        # 1. Obtener sesiones de hoy
        sesiones = await RepositorioSesiones.listar_sesiones_de_hoy_por_materia(db, id_materia)
        if not sesiones:
            return []
            
        ids_sesiones = [s.id_sesion for s in sesiones]
        
        # 2. Obtener asistencias
        asistencias = await RepositorioAsistencias.listar_asistencias_por_lista_sesiones(db, ids_sesiones)
        return asistencias

