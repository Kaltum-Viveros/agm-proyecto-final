# AGM Backend - Plataforma de Gestión Escolar

## Descripción del Proyecto
AGM es una plataforma de gestión escolar basada en una arquitectura de microservicios. El backend expone APIs REST para el consumo desde el frontend y/o clientes como Postman, utilizando una comunicación híbrida e interna entre los distintos microservicios. 

La arquitectura interna actual utiliza **RabbitMQ** como canal principal de eventos asíncronos y conserva **gRPC** como mecanismo de respaldo (fallback) para mantener la compatibilidad durante la migración gradual hacia una comunicación completamente orientada a eventos.

## Integrantes y Roles
El equipo responsable de la planeación, desarrollo y despliegue está conformado por:

- **Kaltum Abdala Viveros Gomez**: Líder del equipo y desarrollador de microservicios.
- **Nelson Ricardo Sosa Francisco**: DBA / Arquitecto de datos y desarrollador de microservicios.
- **Josue Saul Torres Zamora**: DevOps / Despliegue y desarrollador de microservicios.
- **Andy Perez Pavón**: QA / Testing y desarrollador de microservicios.
- **Diego Alberto Nava Rivera**: Desarrollador de microservicios.
- **Esmeralda Urbina Cinto**: Desarrollador de microservicios.

## Stack Tecnológico
- **Lenguaje:** Python
- **Framework REST:** FastAPI
- **Comunicación Síncrona:** gRPC
- **Comunicación Asíncrona (Broker):** RabbitMQ
- **Bases de Datos:** PostgreSQL (bases de datos independientes por microservicio)
- **ORM:** SQLAlchemy (Async)
- **Contenedores:** Docker y Docker Compose
- **Servidores de Aplicación:** Uvicorn / Gunicorn

## Prerrequisitos
Para ejecutar este proyecto de forma local, necesitas tener instalado:
- **Docker** y **Docker Compose**
- **Git** (Opcional, para el clonado del repositorio)
- **Postman** (Recomendado para probar las colecciones de los flujos adjuntos)

## Instrucciones de Instalación Local
Para levantar todo el ecosistema de microservicios, bases de datos y el broker de RabbitMQ de forma local, ejecuta el siguiente comando en la raíz del proyecto:

```bash
docker compose up -d --build
```

Para verificar el estado de los contenedores, ejecuta:
```bash
docker compose ps
```

*Nota: La interfaz de administración de RabbitMQ estará disponible en `http://localhost:15673` (Credenciales por defecto: `agm` / `agm_password`).*

## Instrucciones de Configuración de Variables de Entorno
El proyecto requiere de un archivo de variables de entorno maestro para funcionar correctamente al construir los contenedores.
1. Copia el archivo de ejemplo para crear el tuyo:
   ```bash
   cp .env.example .env
   ```
2. Abre el archivo `.env` en tu editor preferido y ajusta las contraseñas de las bases de datos, llaves secretas para JWT, parámetros de conexión SMTP y demás credenciales necesarias para tu entorno.

## URL de Producción de cada Microservicio
En un entorno local o directamente por contenedor, las APIs se exponen en los siguientes puertos base:

- **MS-1 Auth**: `http://localhost:8001`
- **MS-2 Periodos y Materias**: `http://localhost:8002`
- **MS-3 Docentes y Alumnos**: `http://localhost:8003`
- **MS-4 Calificaciones**: `http://localhost:8004`
- **MS-5 Asistencias**: `http://localhost:8005`
- **MS-6 Notificaciones**: `http://localhost:8006`
- **MS-7 Reportes**: `http://localhost:8007`

*(En el entorno productivo desplegado usando el archivo `docker-compose.prod.yml`, estos servicios se orquestan detrás de un API Gateway (Nginx) que expone los recursos a través de los puertos estándar HTTP/HTTPS (80/443).*

## URL del Video Demostrativo
🎥 [Inserta aquí el enlace a tu video demostrativo de YouTube, Drive o plataforma elegida]

## Estructura del Repositorio
La arquitectura del proyecto está organizada en los siguientes módulos y carpetas:

- `ms-auth/`: Microservicio para la autenticación de usuarios, manejo de sesiones y emisión de tokens JWT.
- `ms-periodos-materias/`: Microservicio para el control del catálogo de materias, planes de estudio y periodos académicos.
- `ms-docentes-alumnos/`: Microservicio encargado del catálogo, registros e información de docentes y alumnos.
- `ms-calificaciones/`: Microservicio para la gestión de actividades, configuraciones de ponderaciones y registro de notas.
- `ms-asistencias/`: Microservicio para la generación y gestión de pases de lista mediante tokens QR.
- `ms-notificaciones/`: Microservicio especializado (worker) encargado de despachar notificaciones y correos electrónicos.
- `ms-reportes/`: Microservicio de consulta para exportación de información estadística y descargas (PDF/Excel).
- `shared/`: Código base, librerías o utilidades transversales compartidas entre los distintos microservicios.
- `proto/`: Archivos `.proto` que definen los esquemas de comunicación y servicios para la implementación de gRPC.
- `docs/`: Documentación técnica de la arquitectura interna.
- `*.postman_collection.json`: Colecciones completas de Postman con los flujos de negocio listos para realizar demostraciones (Docente, Alumno, Admin).
- `docker-compose.yml`: Archivo de orquestación local para levantar todo el backend en modo desarrollo.
- `docker-compose.prod.yml`: Archivo de orquestación optimizado para el despliegue en entornos de producción con el Gateway Nginx.
