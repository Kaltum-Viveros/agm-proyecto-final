# Respaldo y Guía de Despliegue en Railway (AGM Proyecto Final)

Este directorio contiene todo lo necesario para restaurar tu proyecto en Railway desde cero, en caso de que decidas borrarlo para evitar los cobros de base de datos y memoria.

## ¿Qué hay en esta carpeta?
- `variables-backup.json`: Un archivo JSON con TODAS las variables de entorno, dominios privados, dominios públicos y configuraciones de cada uno de los microservicios, api-gateway, postgres y RabbitMQ.
- `restaurar_servicios.ps1`: Un script automatizado en PowerShell que configurará las variables de entorno en todos los servicios de Railway.

---

## Pasos para redesplegar desde cero

Si eliminas el proyecto actual, sigue estos pasos para volver a montar todo:

### 1. Crear el proyecto e instanciar servicios base
1. Ve a tu panel de Railway y crea un **Nuevo Proyecto**.
2. Añade **PostgresSQL** (add plugin -> database).
3. Añade **RabbitMQ** (add template -> rabbitmq o despliega la imagen de Docker).

### 2. Crear los servicios vacíos y enlazar Github
En el panel de Railway, haz click en **New -> GitHub Repo** y selecciona tu repositorio. 
Haz este proceso **8 veces**, una por cada microservicio. 
Renombra cada servicio en Railway (en Settings > General > Name) exactamente con los siguientes nombres:
- `api-gateway`
- `ms-auth`
- `agm-periodos-materias`
- `agm-docentes-alumnos`
- `ms-calificaciones`
- `ms-asistencias`
- `ms-notificaciones`
- `ms-reportes`

### 3. Configurar Dominios (Settings > Networking)
- A **`api-gateway`**, genérale un dominio público (Public Domain).
- A **`ms-notificaciones`**, genérale un dominio público (Public Domain).
- Para el resto de servicios, asegúrate de que tengan un **Private Domain** (Railway los asigna automáticamente).
> **Importante:** Toma nota de cuáles fueron los nuevos "Private Domains" de tus servicios si llegaron a cambiar y del "Private URL" de tu nueva base de datos y tu nuevo RabbitMQ.

### 4. Ejecutar el script automático
Dado que ahora las contraseñas de RabbitMQ y Postgres cambiarán, el script te pedirá que introduzcas las nuevas URLs base.

1. Abre tu terminal (PowerShell) y ve a esta carpeta:
   ```powershell
   cd "railway-backup"
   ```
2. Inicia sesión en Railway si no lo has hecho:
   ```powershell
   railway login
   railway link
   ```
   *(Selecciona tu nuevo proyecto)*
3. Ejecuta el script:
   ```powershell
   .\restaurar_servicios.ps1
   ```
4. El script te preguntará la URL base de tu nuevo Postgres y tu nuevo RabbitMQ, y se encargará de inyectar las más de 60 variables de entorno necesarias en los 8 servicios. Además configurará el `RAILWAY_DOCKERFILE_PATH` en cada uno para que Railway sepa qué Dockerfile compilar de tu monorepo.

### 5. Desplegar
Una vez inyectadas las variables, Railway reiniciará los servicios automáticamente leyendo sus respectivos Dockerfile. Listo, tu sistema estará funcionando de nuevo.
