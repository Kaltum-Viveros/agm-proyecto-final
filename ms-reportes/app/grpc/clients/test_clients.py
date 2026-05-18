"""
Script de prueba para los clientes gRPC del MS-7.
Este script se puede ejecutar localmente (dentro del contenedor o con las variables 
de entorno correctas) para validar la conexión con otros microservicios.
"""
import sys
from pathlib import Path

# Asegurar que la raíz de la app esté en el path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from app.grpc.clients import (
    periodos_materias_client,
    docentes_alumnos_client,
    calificaciones_client,
    asistencias_client
)

def test_periodos_materias():
    print("--- Probando MS-2 (Periodos y Materias) ---")
    res = periodos_materias_client.get_periodo_activo()
    print(f"Respuesta get_periodo_activo: {res}")

def test_docentes_alumnos():
    print("--- Probando MS-3 (Docentes y Alumnos) ---")
    res = docentes_alumnos_client.get_alumno_by_id(alumno_id="uuid-fake")
    print(f"Respuesta get_alumno_by_id: {res}")
    res_m = docentes_alumnos_client.get_materias_by_alumno(alumno_id="uuid-fake")
    print(f"Respuesta get_materias_by_alumno: {res_m}")

def test_calificaciones():
    print("--- Probando MS-4 (Calificaciones) ---")
    res = calificaciones_client.get_estadisticas_materia(materia_id="uuid-fake")
    print(f"Respuesta get_estadisticas_materia: {res}")

def test_asistencias():
    print("--- Probando MS-5 (Asistencias) ---")
    res = asistencias_client.get_estadisticas_asistencia(id_materia="uuid-fake")
    print(f"Respuesta get_estadisticas_asistencia type: {type(res)}")
    print(f"Respuesta get_estadisticas_asistencia: {res.total_sesiones_impartidas if res else 'None'}")
    res_m = asistencias_client.get_asistencias_materia(id_materia="uuid-fake")
    print(f"Respuesta get_asistencias_materia type: {type(res_m)}")
    print(f"Respuesta get_asistencias_materia len: {len(res_m.asistencias) if res_m else 'None'}")

if __name__ == "__main__":
    test_periodos_materias()
    test_docentes_alumnos()
    test_calificaciones()
    test_asistencias()
