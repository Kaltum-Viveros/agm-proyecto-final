# A) Service names
SERVICE_AUTH = "ms-auth"
SERVICE_PERIODOS_MATERIAS = "ms-periodos-materias"
SERVICE_DOCENTES_ALUMNOS = "ms-docentes-alumnos"
SERVICE_CALIFICACIONES = "ms-calificaciones"
SERVICE_ASISTENCIAS = "ms-asistencias"
SERVICE_NOTIFICACIONES = "ms-notificaciones"
SERVICE_REPORTES = "ms-reportes"

# B) Communication modes
COMMUNICATION_MODE_RABBIT = "rabbit"
COMMUNICATION_MODE_GRPC = "grpc"
COMMUNICATION_MODE_HYBRID = "hybrid"

# C) Exchanges
EXCHANGE_RPC = "agm.rpc"
EXCHANGE_EVENTS = "agm.events"
EXCHANGE_EVENTS_DLX = "agm.events.dlx"
EXCHANGE_DLX = "agm.dlx"

# D) RPC queues
QUEUE_AUTH_RPC = "auth.rpc.q"
QUEUE_PERIODOS_MATERIAS_RPC = "periodos_materias.rpc.q"
QUEUE_DOCENTES_ALUMNOS_RPC = "docentes_alumnos.rpc.q"
QUEUE_CALIFICACIONES_RPC = "calificaciones.rpc.q"
QUEUE_ASISTENCIAS_RPC = "asistencias.rpc.q"
QUEUE_REPORTES_RPC = "reportes.rpc.q"

# E) Event queues
QUEUE_NOTIFICACIONES_EVENTS = "notificaciones.events.q"
QUEUE_NOTIFICACIONES_EVENTS_DLQ = "notificaciones.events.dlq"

# F) Auth RPC routing keys
RPC_AUTH_VALIDATE_TOKEN = "rpc.auth.validate_token"
RPC_AUTH_GET_USER_BY_ID = "rpc.auth.get_user_by_id"
RPC_AUTH_CHECK_ROLE = "rpc.auth.check_role"
RPC_AUTH_CREATE_OR_GET_USER_IDENTITY = "rpc.auth.create_or_get_user_identity"
RPC_AUTH_CREATE_PASSWORD_RESET_TOKEN = "rpc.auth.create_password_reset_token"

# G) Periodos/Materias RPC routing keys
RPC_PERIODOS_GET_MATERIA_BY_ID = "rpc.periodos.get_materia_by_id"
RPC_PERIODOS_GET_MATERIA_BY_NRC = "rpc.periodos.get_materia_by_nrc"
RPC_PERIODOS_GET_MATERIAS_BY_DOCENTE = "rpc.periodos.get_materias_by_docente"
RPC_PERIODOS_GET_PERIODO_ACTIVO = "rpc.periodos.get_periodo_activo"

# H) Docentes/Alumnos RPC routing keys
RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA = "rpc.docentes.get_alumnos_by_materia"
RPC_DOCENTES_IS_ALUMNO_EN_MATERIA = "rpc.docentes.is_alumno_en_materia"
RPC_DOCENTES_GET_MATERIAS_BY_ALUMNO = "rpc.docentes.get_materias_by_alumno"
RPC_DOCENTES_GET_ALUMNO_BY_ID = "rpc.docentes.get_alumno_by_id"
RPC_DOCENTES_GET_DOCENTE_BY_ID = "rpc.docentes.get_docente_by_id"
RPC_DOCENTES_GET_DOCENTE_BY_NOMBRE = "rpc.docentes.get_docente_by_nombre"
RPC_DOCENTES_GET_DOCENTE_BY_EMAIL = "rpc.docentes.get_docente_by_email"
RPC_DOCENTES_GET_ALUMNO_BY_EMAIL = "rpc.docentes.get_alumno_by_email"

# I) Calificaciones RPC routing keys
RPC_CALIFICACIONES_GET_CONCENTRADO = "rpc.calificaciones.get_concentrado"
RPC_CALIFICACIONES_GET_PROMEDIO_ALUMNO = "rpc.calificaciones.get_promedio_alumno"
RPC_CALIFICACIONES_GET_ESTADISTICAS_MATERIA = "rpc.calificaciones.get_estadisticas_materia"

# J) Asistencias RPC routing keys
RPC_ASISTENCIAS_GET_ASISTENCIA_ALUMNO = "rpc.asistencias.get_asistencia_alumno"
RPC_ASISTENCIAS_GET_ASISTENCIAS_MATERIA = "rpc.asistencias.get_asistencias_materia"
RPC_ASISTENCIAS_GET_ESTADISTICAS_ASISTENCIA = "rpc.asistencias.get_estadisticas_asistencia"

# K) Notification event routing keys
EVENT_NOTIFICACIONES_BIENVENIDA = "event.notificaciones.bienvenida"
EVENT_NOTIFICACIONES_BIENVENIDA_ALUMNO = "event.notificaciones.bienvenida_alumno"
EVENT_NOTIFICACIONES_BIENVENIDA_DOCENTE = "event.notificaciones.bienvenida_docente"
EVENT_NOTIFICACIONES_BAJA = "event.notificaciones.baja"
EVENT_NOTIFICACIONES_BAJA_ALUMNO = "event.notificaciones.baja_alumno"
EVENT_NOTIFICACIONES_CIERRE_MATERIA = "event.notificaciones.cierre_materia"
EVENT_NOTIFICACIONES_RESET_PASSWORD = "event.notificaciones.reset_password"
EVENT_NOTIFICACIONES_DLQ = "event.notificaciones.dlq"

EVENT_ROUTING_KEYS_BY_TARGET = {
    SERVICE_NOTIFICACIONES: [
        EVENT_NOTIFICACIONES_BIENVENIDA_ALUMNO,
        EVENT_NOTIFICACIONES_BIENVENIDA_DOCENTE,
        EVENT_NOTIFICACIONES_BAJA_ALUMNO,
        EVENT_NOTIFICACIONES_CIERRE_MATERIA,
        EVENT_NOTIFICACIONES_RESET_PASSWORD,
    ],
}

# L) General domain events for future use
EVENT_ALUMNO_IMPORTADO = "event.alumnos.importado"
EVENT_MATERIA_CERRADA = "event.materia.cerrada"
EVENT_ASISTENCIA_REGISTRADA = "event.asistencia.registrada"

# 3) Maps
RPC_QUEUES_BY_SERVICE = {
    SERVICE_AUTH: QUEUE_AUTH_RPC,
    SERVICE_PERIODOS_MATERIAS: QUEUE_PERIODOS_MATERIAS_RPC,
    SERVICE_DOCENTES_ALUMNOS: QUEUE_DOCENTES_ALUMNOS_RPC,
    SERVICE_CALIFICACIONES: QUEUE_CALIFICACIONES_RPC,
    SERVICE_ASISTENCIAS: QUEUE_ASISTENCIAS_RPC,
    SERVICE_REPORTES: QUEUE_REPORTES_RPC,
}

EVENT_QUEUES_BY_SERVICE = {
    SERVICE_NOTIFICACIONES: QUEUE_NOTIFICACIONES_EVENTS,
}

RPC_ROUTING_KEYS_BY_TARGET = {
    SERVICE_AUTH: [
        RPC_AUTH_VALIDATE_TOKEN,
        RPC_AUTH_GET_USER_BY_ID,
        RPC_AUTH_CHECK_ROLE,
        RPC_AUTH_CREATE_OR_GET_USER_IDENTITY,
        RPC_AUTH_CREATE_PASSWORD_RESET_TOKEN,
    ],
    SERVICE_PERIODOS_MATERIAS: [
        RPC_PERIODOS_GET_MATERIA_BY_ID,
        RPC_PERIODOS_GET_MATERIA_BY_NRC,
        RPC_PERIODOS_GET_MATERIAS_BY_DOCENTE,
        RPC_PERIODOS_GET_PERIODO_ACTIVO,
    ],
    SERVICE_DOCENTES_ALUMNOS: [
        RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA,
        RPC_DOCENTES_IS_ALUMNO_EN_MATERIA,
        RPC_DOCENTES_GET_MATERIAS_BY_ALUMNO,
        RPC_DOCENTES_GET_ALUMNO_BY_ID,
        RPC_DOCENTES_GET_DOCENTE_BY_ID,
        RPC_DOCENTES_GET_DOCENTE_BY_NOMBRE,
        RPC_DOCENTES_GET_DOCENTE_BY_EMAIL,
        RPC_DOCENTES_GET_ALUMNO_BY_EMAIL,
    ],
    SERVICE_CALIFICACIONES: [
        RPC_CALIFICACIONES_GET_CONCENTRADO,
        RPC_CALIFICACIONES_GET_PROMEDIO_ALUMNO,
        RPC_CALIFICACIONES_GET_ESTADISTICAS_MATERIA,
    ],
    SERVICE_ASISTENCIAS: [
        RPC_ASISTENCIAS_GET_ASISTENCIA_ALUMNO,
        RPC_ASISTENCIAS_GET_ASISTENCIAS_MATERIA,
        RPC_ASISTENCIAS_GET_ESTADISTICAS_ASISTENCIA,
    ],
}
