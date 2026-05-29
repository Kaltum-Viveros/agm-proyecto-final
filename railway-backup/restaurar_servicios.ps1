param(
    [string]$PostgresURL,
    [string]$RabbitMQURL
)

Write-Host "========================================="
Write-Host "Restaurador de Variables AGM - Railway CLI"
Write-Host "========================================="
Write-Host ""

if (-not $PostgresURL) {
    Write-Host "Por favor, ve a tu panel de Railway -> Postgres -> Connect -> Copia la 'Postgres Connection URL' (solo hasta el puerto 5432, SIN el nombre de la bd al final)"
    Write-Host "Ejemplo: postgresql://postgres:PASSWORD@postgres.railway.internal:5432"
    $PostgresURL = Read-Host "URL Base de Postgres"
}

if (-not $RabbitMQURL) {
    Write-Host ""
    Write-Host "Por favor, ve a tu panel de Railway -> RabbitMQ -> Variables -> Copia el valor de RABBITMQ_URL"
    Write-Host "Ejemplo: amqp://USER:PASSWORD@rabbitmq.railway.internal:5672"
    $RabbitMQURL = Read-Host "URL de RabbitMQ"
}

# Quitar el slash al final si el usuario lo puso por accidente
$PostgresURL = $PostgresURL.TrimEnd("/")

Write-Host "`n[1/8] Configurando api-gateway..."
railway variables set PORT=80 RAILWAY_DOCKERFILE_PATH=infra/nginx/Dockerfile --service api-gateway

Write-Host "`n[2/8] Configurando ms-auth..."
railway variables set APP_NAME=ms-auth COMMUNICATION_MODE=hybrid CORS_ALLOWED_ORIGINS=https://app-agm.railway.app CORS_ORIGINS=https://app-agm.railway.app DATABASE_URL="$PostgresURL/agm_auth_db" ENVIRONMENT=production GRPC_HOST=0.0.0.0 GRPC_PORT=50051 JWT_SECRET_KEY=<YOUR_JWT_SECRET> NOTIFICACIONES_GRPC_HOST=ms-notificaciones.railway.internal NOTIFICACIONES_GRPC_PORT=50056 PORT=8001 RABBITMQ_RPC_TIMEOUT_SECONDS=5 RABBITMQ_URL="$RabbitMQURL" RAILWAY_DOCKERFILE_PATH=ms-auth/Dockerfile REST_HOST=0.0.0.0 REST_PORT=8001 SEED_ADMIN_EMAIL=admin@agm.com "SEED_ADMIN_NAME=Administrador AGM" SEED_ADMIN_PASSWORD=Admin12345 --service ms-auth

Write-Host "`n[3/8] Configurando agm-periodos-materias..."
railway variables set APP_NAME=ms-periodos-materias COMMUNICATION_MODE=hybrid CORS_ALLOWED_ORIGINS=https://app-agm.railway.app CORS_ORIGINS=https://app-agm.railway.app DATABASE_URL="postgresql+asyncpg" + $PostgresURL.Substring(10) + "/agm_periodos_db" ENVIRONMENT=production GRPC_HOST=0.0.0.0 GRPC_PORT=50052 MS_AUTH_GRPC_HOST=agm-production.railway.internal PORT=8002 RABBITMQ_URL="$RabbitMQURL" RAILWAY_DOCKERFILE_PATH=ms-periodos-materias/Dockerfile REST_HOST=0.0.0.0 REST_PORT=8002 --service agm-periodos-materias

Write-Host "`n[4/8] Configurando agm-docentes-alumnos..."
railway variables set COMMUNICATION_MODE=hybrid DATABASE_URL="$PostgresURL/agm_docentes_db" GRPC_PORT=50053 MS1_HOST=agm-production.railway.internal MS1_PORT=50051 PERIODOS_GRPC_HOST=ms-periodos-materias.railway.internal PERIODOS_GRPC_PORT=50052 PORT=8003 RABBITMQ_URL="$RabbitMQURL" RAILWAY_DOCKERFILE_PATH=ms-docentes-alumnos/Dockerfile REST_PORT=8003 --service agm-docentes-alumnos

Write-Host "`n[5/8] Configurando ms-calificaciones..."
railway variables set APP_NAME=ms-calificaciones COMMUNICATION_MODE=hybrid CORS_ALLOWED_ORIGINS=https://app-agm.railway.app CORS_ORIGINS=https://app-agm.railway.app DATABASE_URL="$PostgresURL/agm_calificaciones_db" DOCENTES_GRPC_HOST=agm-docentes.railway.internal DOCENTES_GRPC_PORT=50053 ENVIRONMENT=production GRPC_HOST=0.0.0.0 GRPC_PORT=50054 MS_AUTH_GRPC_HOST=agm-production.railway.internal PERIODOS_GRPC_HOST=agm-periodos-materias.railway.internal PERIODOS_GRPC_PORT=50052 PORT=8004 RABBITMQ_URL="$RabbitMQURL" RAILWAY_DOCKERFILE_PATH=ms-calificaciones/Dockerfile REST_HOST=0.0.0.0 REST_PORT=8004 --service ms-calificaciones

Write-Host "`n[6/8] Configurando ms-asistencias..."
railway variables set ALUMNOS_GRPC_HOST=agm-docentes.railway.internal ALUMNOS_GRPC_PORT=50053 AUTH_GRPC_HOST=ms-auth.railway.internal AUTH_GRPC_PORT=50051 COMMUNICATION_MODE=hybrid CORS_ORIGINS=https://app-agm.railway.app DATABASE_URL="postgresql+asyncpg" + $PostgresURL.Substring(10) + "/agm_asistencias_db" ENVIRONMENT=production MATERIAS_GRPC_HOST=agm-periodos-materias.railway.internal MATERIAS_GRPC_PORT=50052 PORT=8005 PRESENT_LIMIT_MINUTES=5 "QR_SECRET_KEY=<YOUR_QR_SECRET>" QR_TTL_SECONDS=20 RABBITMQ_EXCHANGE_DLX=agm.dlx RABBITMQ_EXCHANGE_EVENTS=agm.events RABBITMQ_EXCHANGE_RPC=agm.rpc RABBITMQ_RPC_TIMEOUT_SECONDS=5 RABBITMQ_URL="$RabbitMQURL" RAILWAY_DOCKERFILE_PATH=ms-asistencias/Dockerfile --service ms-asistencias

Write-Host "`n[7/8] Configurando ms-notificaciones..."
railway variables set APP_NAME=ms-notificaciones DATABASE_URL="postgresql+psycopg" + $PostgresURL.Substring(10) + "/agm_notificaciones_db" ENVIRONMENT=production GRPC_HOST=0.0.0.0 GRPC_PORT=50056 PORT=8006 RABBITMQ_URL="$RabbitMQURL" RAILWAY_DOCKERFILE_PATH=ms-notificaciones/Dockerfile REST_HOST=0.0.0.0 REST_PORT=8006 --service ms-notificaciones

Write-Host "`n[8/8] Configurando ms-reportes..."
railway variables set ALUMNOS_GRPC_HOST=ms-docentes-alumnos.railway.internal ALUMNOS_GRPC_PORT=50053 API_V1_PREFIX=/api/v1 ASISTENCIAS_GRPC_HOST=ms-asistencias.railway.internal ASISTENCIAS_GRPC_PORT=50055 AUTH_GRPC_HOST=ms-auth.railway.internal AUTH_GRPC_PORT=50051 CALIFICACIONES_GRPC_HOST=ms-calificaciones.railway.internal CALIFICACIONES_GRPC_PORT=50054 COMMUNICATION_MODE=hybrid CORS_ALLOWED_ORIGINS=https://app-agm.railway.app DATABASE_URL="postgresql+asyncpg" + $PostgresURL.Substring(10) + "/agm_reportes_db" DEBUG=false ENVIRONMENT=production GRPC_HOST=0.0.0.0 GRPC_PORT=50057 MATERIAS_GRPC_HOST=agm-periodos-materias.railway.internal MATERIAS_GRPC_PORT=50052 PORT=8007 RABBITMQ_EXCHANGE_DLX=agm.dlx RABBITMQ_EXCHANGE_EVENTS=agm.events RABBITMQ_EXCHANGE_RPC=agm.rpc RABBITMQ_RPC_TIMEOUT_SECONDS=5 RABBITMQ_URL="$RabbitMQURL" RAILWAY_DOCKERFILE_PATH=ms-reportes/Dockerfile REST_HOST=0.0.0.0 REST_PORT=8007 SERVICE_NAME=ms-reportes --service ms-reportes

Write-Host "`n========================================="
Write-Host "Todas las variables han sido inyectadas."
Write-Host "Railway empezará a construir y desplegar tus servicios usando los Dockerfile especificados."
Write-Host "No olvides configurar los dominios públicos para api-gateway y ms-notificaciones en la interfaz web."
Write-Host "========================================="
