import grpc
from app.grpc.generated import docentes_alumnos_pb2, docentes_alumnos_pb2_grpc
from app.models.inscripcion import Inscripcion
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

class DocentesAlumnosService(docentes_alumnos_pb2_grpc.DocentesAlumnosServiceServicer):
    
    def GetAlumnosByMateria(self, request, context):
        """Devuelve la lista de alumnos inscritos en una materia (para MS-4/MS-5)"""
        db = SessionLocal()
        try:
            # Consultamos las inscripciones filtrando por materia_id
            inscripciones = db.query(Inscripcion).filter(
                Inscripcion.materia_id == request.materia_id,
                Inscripcion.activa == True
            ).all()

            alumnos_list = []
            for ins in inscripciones:
                alumno = ins.alumno
                alumnos_list.append(docentes_alumnos_pb2.AlumnoProfile(
                    alumno_id=str(alumno.alumno_id),
                    nombre_completo=alumno.nombre_completo,
                    matricula=alumno.matricula,
                    correo=alumno.correo
                ))

            return docentes_alumnos_pb2.AlumnosResponse(alumnos=alumnos_list)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno: {str(e)}")
            return docentes_alumnos_pb2.AlumnosResponse()
        finally:
            db.close()