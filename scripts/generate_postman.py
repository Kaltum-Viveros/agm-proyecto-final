import json
import os

env = {
  "id": "0cb560fb-ca12-4f9a-913d-cca0292e1b05",
  "name": "AGM Local Completo",
  "values": [
    {"key": "base_url_auth", "value": "http://localhost:8001", "enabled": True},
    {"key": "base_url_periodos", "value": "http://localhost:8002", "enabled": True},
    {"key": "base_url_docentes_alumnos", "value": "http://localhost:8003", "enabled": True},
    {"key": "base_url_calificaciones", "value": "http://localhost:8004", "enabled": True},
    
    # Admin
    {"key": "auth_admin_email", "value": "admin@agm.com", "enabled": True},
    {"key": "auth_admin_password", "value": "Admin12345", "enabled": True},
    {"key": "admin_access_token", "value": "", "enabled": True},

    # Docente
    {"key": "docente_email", "value": "juan.perez@agm.com", "enabled": True},
    {"key": "docente_password", "value": "", "enabled": True},
    {"key": "docente_user_id", "value": "", "enabled": True},
    {"key": "docente_id", "value": "", "enabled": True},
    {"key": "docente_access_token", "value": "", "enabled": True},

    # Alumno
    {"key": "alumno_email", "value": "maria.gomez@agm.com", "enabled": True},
    {"key": "alumno_password", "value": "", "enabled": True},
    {"key": "alumno_user_id", "value": "", "enabled": True},
    {"key": "alumno_id", "value": "", "enabled": True},
    {"key": "alumno_access_token", "value": "", "enabled": True},
    
    # MS2 / General
    {"key": "periodo_id", "value": "", "enabled": True},
    {"key": "plan_estudio_id", "value": "", "enabled": True},
    {"key": "materia_catalogo_id", "value": "", "enabled": True},
    {"key": "materia_ofertada_id", "value": "", "enabled": True},

    # MS4
    {"key": "ponderacion_id", "value": "", "enabled": True},
    {"key": "actividad_id", "value": "", "enabled": True},
    {"key": "calificacion_id", "value": "", "enabled": True},
  ],
  "_postman_variable_scope": "environment"
}

def create_request(name, method, url, auth_token_var, body=None, test_script=None, extra_headers=None):
    req = {
        "name": name,
        "request": {
            "method": method,
            "header": [],
            "url": {
                "raw": url,
                "host": [url]
            }
        }
    }
    if auth_token_var:
        req["request"]["header"].append({"key": "Authorization", "value": f"Bearer {auth_token_var}", "type": "text"})
    
    req["request"]["header"].append({"key": "Content-Type", "value": "application/json", "type": "text"})
    
    if extra_headers:
        req["request"]["header"].extend(extra_headers)
    
    if body is not None:
        req["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, indent=2),
            "options": {"raw": {"language": "json"}}
        }
        
    if test_script:
        req["event"] = [{
            "listen": "test",
            "script": {
                "type": "text/javascript",
                "exec": test_script
            }
        }]
    return req

# Test scripts
test_status_200_201 = ["pm.test('Status 200 or 201', function () { pm.expect(pm.response.code).to.be.oneOf([200, 201]); });"]

admin_login_test = test_status_200_201 + [
    "var jsonData = pm.response.json();",
    "pm.environment.set('admin_access_token', jsonData.data.access_token);"
]
docente_login_test = test_status_200_201 + [
    "var jsonData = pm.response.json();",
    "pm.environment.set('docente_access_token', jsonData.data.access_token);"
]
alumno_login_test = test_status_200_201 + [
    "var jsonData = pm.response.json();",
    "pm.environment.set('alumno_access_token', jsonData.data.access_token);"
]

crear_identidad_docente_test = test_status_200_201 + [
    "var jsonData = pm.response.json();",
    "pm.environment.set('docente_user_id', jsonData.data.user.user_id);",
    "pm.environment.set('docente_password', jsonData.data.temporary_password);"
]

crear_identidad_alumno_test = test_status_200_201 + [
    "var jsonData = pm.response.json();",
    "pm.environment.set('alumno_user_id', jsonData.data.user.user_id);",
    "pm.environment.set('alumno_password', jsonData.data.temporary_password);"
]

collection = {
  "info": {
    "_postman_id": "47a0e716-d57a-4c17-917c-eb4e5ab08cf5",
    "name": "AGM E2E Completa (MS1 - MS4)",
    "description": "Flujo E2E desde MS-1 hasta MS-4 con creación de identidades reales en Auth, materias, asignaciones en BD y flujo de calificaciones.",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "0. Pre-Requisitos y Logins (MS-Auth)",
      "item": [
        create_request("1. Admin Login", "POST", "{{base_url_auth}}/auth/login", "",
                       body={"email": "{{auth_admin_email}}", "contrasena": "{{auth_admin_password}}"},
                       test_script=admin_login_test),
        create_request("2. Crear Identidad Docente", "POST", "{{base_url_auth}}/auth/users", "{{admin_access_token}}",
                       body={"nombre_completo": "Juan Perez", "email": "{{docente_email}}", "rol": "DOCENTE"},
                       test_script=crear_identidad_docente_test),
        create_request("3. Crear Identidad Alumno", "POST", "{{base_url_auth}}/auth/users", "{{admin_access_token}}",
                       body={"nombre_completo": "Maria Gomez", "email": "{{alumno_email}}", "rol": "ALUMNO"},
                       test_script=crear_identidad_alumno_test),
        create_request("4. Docente Login", "POST", "{{base_url_auth}}/auth/login", "",
                       body={"email": "{{docente_email}}", "contrasena": "{{docente_password}}"},
                       test_script=docente_login_test),
        create_request("5. Alumno Login", "POST", "{{base_url_auth}}/auth/login", "",
                       body={"email": "{{alumno_email}}", "contrasena": "{{alumno_password}}"},
                       test_script=alumno_login_test)
      ]
    },
    {
      "name": "1. Estructura Académica (MS-Periodos)",
      "item": [
        create_request("1. Crear Periodo", "POST", "{{base_url_periodos}}/api/v1/periodos", "{{admin_access_token}}",
                       body={"nombre": "Primavera 2026", "fecha_inicio": "2026-01-01", "fecha_fin": "2026-06-30", "activo": True},
                       test_script=test_status_200_201 + ["var j = pm.response.json(); pm.environment.set('periodo_id', j.data.id || j.data.periodo_id);"]),
        create_request("2. Activar Periodo", "PATCH", "{{base_url_periodos}}/api/v1/periodos/{{periodo_id}}/activar", "{{admin_access_token}}",
                       body={}, test_script=test_status_200_201),
        create_request("3. Crear Plan de Estudio", "POST", "{{base_url_periodos}}/api/v1/planes-estudio", "{{admin_access_token}}",
                       body={"nombre": "Ciencias de la Computacion", "clave": "CC01", "anio": 2026, "activo": True},
                       test_script=test_status_200_201 + ["var j = pm.response.json(); pm.environment.set('plan_estudio_id', j.data.id || j.data.plan_estudio_id);"]),
        create_request("4. Crear Materia Catalogo", "POST", "{{base_url_periodos}}/api/v1/materias-catalogo", "{{admin_access_token}}",
                       body={"nombre": "Servicios Web 2026", "clave": "SW26", "creditos": 6, "activo": True},
                       test_script=test_status_200_201 + ["var j = pm.response.json(); pm.environment.set('materia_catalogo_id', j.data.id || j.data.materia_catalogo_id);"]),
        create_request("5. Crear Materia Ofertada", "POST", "{{base_url_periodos}}/api/v1/materias-ofertadas", "{{admin_access_token}}",
                       body={"periodo_id": "{{periodo_id}}", "materia_catalogo_id": "{{materia_catalogo_id}}", "nrc": "88888", "seccion": "002", "cupo_maximo": 40},
                       test_script=test_status_200_201 + ["var j = pm.response.json(); pm.environment.set('materia_ofertada_id', j.data.id || j.data.materia_ofertada_id);"]),
        create_request("6. Listar Materias (Publico)", "GET", "{{base_url_periodos}}/api/v1/materias", "{{admin_access_token}}",
                       test_script=test_status_200_201)
      ]
    },
    {
      "name": "2. Docentes y Alumnos (MS-Docentes)",
      "item": [
        create_request("1. Crear Docente DB", "POST", "{{base_url_docentes_alumnos}}/api/v1/docentes/", "{{admin_access_token}}",
                       body={"nombre_completo": "Juan Perez", "correo": "{{docente_email}}", "cubiculo": "C-12", "user_id": "{{docente_user_id}}"},
                       test_script=test_status_200_201 + ["var j = pm.response.json(); pm.environment.set('docente_id', j.docente_id);"]),
        create_request("2. Crear Alumno DB", "POST", "{{base_url_docentes_alumnos}}/api/v1/alumnos/", "{{admin_access_token}}",
                       body={"nombre_completo": "Maria Gomez", "correo": "{{alumno_email}}", "matricula": "2026001", "user_id": "{{alumno_user_id}}"},
                       test_script=test_status_200_201 + ["var j = pm.response.json(); pm.environment.set('alumno_id', j.alumno_id);"]),
        create_request("3. Asignar Docente a Materia Ofertada", "PATCH", "{{base_url_periodos}}/api/v1/materias-ofertadas/{{materia_ofertada_id}}/asignar-docente", "{{admin_access_token}}",
                       body={"docente_id": "{{docente_id}}", "docente_nombre": "Juan Perez"},
                       test_script=test_status_200_201),
        create_request("4. Inscribir Alumno a Materia", "POST", "{{base_url_docentes_alumnos}}/api/v1/inscripciones/", "{{admin_access_token}}",
                       body={"docente_id": "{{docente_id}}", "alumno_id": "{{alumno_id}}", "materia_id": "{{materia_ofertada_id}}", "periodo_id": "{{periodo_id}}", "nrc_materia": "88888"},
                       test_script=test_status_200_201)
      ]
    },
    {
      "name": "3. Calificaciones (MS-Calificaciones)",
      "item": [
        create_request("1. Configurar Ponderaciones (Docente)", "POST", "{{base_url_calificaciones}}/api/v1/ponderaciones/{{materia_ofertada_id}}", "{{docente_access_token}}",
                       body={"criterios": [{"nombre": "Examen 1", "porcentaje": 50, "orden": 1}, {"nombre": "Proyecto", "porcentaje": 50, "orden": 2}]},
                       test_script=test_status_200_201 + ["var j = pm.response.json(); pm.environment.set('ponderacion_id', j.data.criterios[0].id);"]),
        create_request("2. Crear Actividad (Docente)", "POST", "{{base_url_calificaciones}}/api/v1/actividades", "{{docente_access_token}}",
                       body={"materia_id": "{{materia_ofertada_id}}", "ponderacion_id": "{{ponderacion_id}}", "nombre": "Evaluación Teórica", "valor_maximo": 10},
                       test_script=test_status_200_201 + ["var j = pm.response.json(); pm.environment.set('actividad_id', j.data.id);"]),
        create_request("3. Registrar Calificacion (Docente)", "POST", "{{base_url_calificaciones}}/api/v1/calificaciones", "{{docente_access_token}}",
                       body={"actividad_id": "{{actividad_id}}", "alumno_id": "{{alumno_id}}", "calificacion": 8.5, "observaciones": "Buen desempeño"},
                       test_script=test_status_200_201 + ["var j = pm.response.json(); pm.environment.set('calificacion_id', j.data.id);"]),
        create_request("4. Obtener Concentrado (Docente)", "GET", "{{base_url_calificaciones}}/api/v1/concentrado/{{materia_ofertada_id}}?modo=actual", "{{docente_access_token}}",
                       test_script=test_status_200_201),
        create_request("5. Ver Calificaciones (Alumno)", "GET", "{{base_url_calificaciones}}/api/v1/calificaciones/alumno/{{alumno_id}}/materia/{{materia_ofertada_id}}", "{{alumno_access_token}}",
                       test_script=test_status_200_201)
      ]
    }
  ]
}

with open("AGM_Local.postman_environment.json", "w", encoding="utf-8") as f:
    json.dump(env, f, indent=2, ensure_ascii=False)

with open("AGM_Microservicios_Locales.postman_collection.json", "w", encoding="utf-8") as f:
    json.dump(collection, f, indent=2, ensure_ascii=False)

print("Archivos de Postman generados con éxito.")
