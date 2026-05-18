from app.services.pdf_generator import generate_calificaciones_pdf
from app.services.excel_generator import generate_calificaciones_excel
import os

class MockAlumno:
    def __init__(self, alumno_id, matricula, nombre_completo):
        self.alumno_id = alumno_id
        self.matricula = matricula
        self.nombre_completo = nombre_completo

class MockConcentrado:
    def __init__(self, alumno_id, promedio_real, promedio_redondeado):
        self.alumno_id = alumno_id
        self.promedio_real = promedio_real
        self.promedio_redondeado = promedio_redondeado

def test_generators():
    materia_data = {
        "nombre": "Física Cuántica",
        "nrc": "12345",
        "seccion": "1A",
        "docente_nombre": "Dr. Juan Pérez",
        "periodo": {"nombre": "Primavera 2026"}
    }
    
    alumnos = [
        MockAlumno("uuid-1", "A01010101", "Ana Gomez"),
        MockAlumno("uuid-2", "A01010102", "Beto Silva")
    ]
    
    concentrado = [
        MockConcentrado("uuid-1", 85.4, 85),
        MockConcentrado("uuid-2", 69.9, 70)
    ]
    
    # Test PDF
    pdf_bytes = generate_calificaciones_pdf(materia_data, alumnos, concentrado)
    assert len(pdf_bytes) > 0, "El PDF generado está vacío."
    
    # Test Excel
    excel_bytes = generate_calificaciones_excel(materia_data, alumnos, concentrado)
    assert len(excel_bytes) > 0, "El Excel generado está vacío."
    
    print("Tests ejecutados correctamente. PDF y Excel generados en memoria.")

if __name__ == "__main__":
    test_generators()
