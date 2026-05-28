# AGM Backend

## Plataforma de Gestión Escolar

AGM es una plataforma de gestión escolar basada en una arquitectura de microservicios. El backend expone APIs REST para consumo desde el frontend o clientes como Postman, y utiliza una comunicación híbrida entre microservicios.

Actualmente, la arquitectura interna utiliza **RabbitMQ** como canal principal de eventos asíncronos y mantiene **gRPC** como mecanismo de respaldo (*fallback*) para conservar la comunicación entre servicios en caso de fallos del bus de mensajes.

---

## Documentación

* Arquitectura RabbitMQ y fallback gRPC
* Pruebas RabbitMQ
* Ejecución rápida

---

## Integrantes y Roles

El equipo responsable de la planeación, desarrollo y despliegue está conformado por:

| Integrante                    | Rol                                                         |
| ----------------------------- | ----------------------------------------------------------- |
| Kaltum Abdala Viveros Gómez   | Líder del equipo y desarrollador de microservicios          |
| Nelson Ricardo Sosa Francisco | DBA / Arquitecto de datos y desarrollador de microservicios |
| Josué Saúl Torres Zamora      | DevOps / Despliegue y desarrollador de microservicios       |
| Andy Pérez Pavón              | QA / Testing y desarrollador de microservicios              |
| Diego Alberto Nava Rivera     | Desarrollador de microservicios                             |
| Esmeralda Urbina Cinto        | Desarrolladora de microservicios                            |

---

## Stack Tecnológico

| Componente               | Tecnología                                             |
| ------------------------ | ------------------------------------------------------ |
| Lenguaje                 | Python                                                 |
| Framework REST           | FastAPI                                                |
| Comunicación síncrona    | gRPC                                                   |
| Comunicación asíncrona   | RabbitMQ                                               |
| Bases de datos           | PostgreSQL, con bases independientes por microservicio |
| ORM                      | SQLAlchemy                                             |
| Contenedores             | Docker y Docker Compose                                |
| Servidores de aplicación | Uvicorn / Gunicorn                                     |

---

## Prerrequisitos

Para ejecutar este proyecto de forma local, es necesario tener instalado:

* Docker y Docker Compose
* Git
* Postman, recomendado para probar las colecciones de flujos

---

## Instalación y Ejecución Local

Para levantar todo el ecosistema de microservicios, bases de datos y RabbitMQ de forma local, ejecuta desde la raíz del proyecto:

```bash
docker compose up -d --build
```

También puedes levantar los contenedores sin reconstruir imágenes:

```bash
docker compose up -d
```

Para verificar el estado de los contenedores:

```bash
docker compose ps
```

---

## RabbitMQ Management UI

La interfaz de administración de RabbitMQ estará disponible en:

```txt
http://localhost:15673
```

Credenciales por defecto:

```txt
Usuario: agm
Contraseña: agm_password
```

Si el entorno local usa los valores por defecto de `.env.example`, el puerto de administración puede estar publicado como `15672`.

Para verificar el puerto efectivo:

```bash
docker compose ps rabbitmq
```

---

## Configuración de Variables de Entorno

El proyecto requiere un archivo de variables de entorno maestro para construir y ejecutar correctamente los contenedores.

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Después, abre el archivo `.env` y ajusta las variables necesarias para tu entorno, como:

* Contraseñas de bases de datos
* Llaves secretas para JWT
* Parámetros de conexión SMTP
* Credenciales necesarias para servicios externos

---

## URLs Locales de los Microservicios

En entorno local, las APIs se exponen en los siguientes puertos:

| Microservicio            | URL                      |
| ------------------------ | ------------------------ |
| MS-1 Auth                | `http://localhost:8001`  |
| MS-2 Periodos y Materias | `http://localhost:8002`  |
| MS-3 Docentes y Alumnos  | `http://localhost:8003`  |
| MS-4 Calificaciones      | `http://localhost:8004`  |
| MS-5 Asistencias         | `http://localhost:8005`  |
| MS-6 Notificaciones      | `http://localhost:8006`  |
| MS-7 Reportes            | `http://localhost:8007`  |
| RabbitMQ Management      | `http://localhost:15673` |

---

## Entorno de Producción

En producción, los servicios se orquestan mediante el archivo:

```txt
docker-compose.prod.yml
```

En este entorno, los microservicios se exponen detrás de un API Gateway con Nginx, utilizando los puertos estándar:

```txt
HTTP: 80
HTTPS: 443
```

---

## Video Demostrativo

🎥 Inserta aquí el enlace al video demostrativo:

```txt
https://youtu.be/ZGupB6umF98
```

---

## Estructura del Repositorio

La arquitectura del proyecto está organizada en los siguientes módulos y carpetas:

```txt
agm-backend/
├── ms-auth/
├── ms-periodos-materias/
├── ms-docentes-alumnos/
├── ms-calificaciones/
├── ms-asistencias/
├── ms-notificaciones/
├── ms-reportes/
├── shared/
├── proto/
├── docs/
├── docker-compose.yml
├── docker-compose.prod.yml
└── *.postman_collection.json
```

---

## Descripción de Módulos

### `ms-auth/`

Microservicio encargado de la autenticación de usuarios, manejo de sesiones, emisión de tokens JWT y control de roles.

---

### `ms-periodos-materias/`

Microservicio encargado del control de periodos académicos, catálogo de materias, planes de estudio y materias asignadas.

---

### `ms-docentes-alumnos/`

Microservicio encargado del catálogo, registro e información académica de docentes y alumnos.

---

### `ms-calificaciones/`

Microservicio encargado de la gestión de ponderaciones, actividades evaluables, registro de calificaciones y cálculo de concentrados.

---

### `ms-asistencias/`

Microservicio encargado de la generación y gestión de pases de lista mediante tokens QR.

---

### `ms-notificaciones/`

Microservicio especializado en el envío de notificaciones y correos electrónicos transaccionales.

---

### `ms-reportes/`

Microservicio encargado de generar reportes, estadísticas y exportaciones en formatos como PDF o Excel.

---

### `shared/`

Código base, librerías o utilidades compartidas entre los microservicios.

---

### `proto/`

Archivos `.proto` que definen los contratos de comunicación para gRPC.

---

### `docs/`

Documentación técnica de la arquitectura interna del backend.

---

### `*.postman_collection.json`

Colecciones de Postman con flujos de negocio para pruebas y demostraciones, incluyendo flujos de administrador, docente y alumno.

---

## Comunicación entre Microservicios

El sistema utiliza una comunicación híbrida:

* **RabbitMQ** como canal principal para eventos asíncronos.
* **gRPC** como mecanismo de respaldo en caso de fallos del bus.
* **REST** para interacción con el frontend y clientes externos.

Esta arquitectura permite mantener los microservicios desacoplados, con bases de datos independientes y comunicación interna controlada mediante eventos y contratos definidos.

---

## Comandos Útiles

Levantar todos los servicios:

```bash
docker compose up -d --build
```

Levantar servicios sin reconstruir:

```bash
docker compose up -d
```

Ver estado de contenedores:

```bash
docker compose ps
```

Detener servicios:

```bash
docker compose down
```

Ver logs de un servicio específico:

```bash
docker compose logs -f nombre-del-servicio
```

Ejemplo:

```bash
docker compose logs -f ms-calificaciones
```

---

## Estado General

El backend de AGM se encuentra organizado en microservicios independientes, cada uno con responsabilidades específicas dentro del dominio escolar. La arquitectura permite escalar, probar y desplegar servicios de forma modular, manteniendo separación entre autenticación, gestión académica, calificaciones, asistencias, notificaciones y reportes.
