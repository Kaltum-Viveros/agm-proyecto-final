import grpc
from app.grpc.generated import docentes_alumnos_pb2, docentes_alumnos_pb2_grpc
from app.models.alumno import Alumno
from app.models.docente import Docente  # Necesario para que SQLAlchemy resuelva el mapper de Inscripcion
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

    def GetAlumnoById(self, request, context):
        """Obtiene perfil de alumno por ID (usado por MS-6)"""
        db = SessionLocal()
        try:
            alumno = db.query(Alumno).filter(Alumno.alumno_id == request.alumno_id).first()
            if not alumno:
                return docentes_alumnos_pb2.AlumnoProfile()
            
            return docentes_alumnos_pb2.AlumnoProfile(
                alumno_id=str(alumno.alumno_id),
                nombre_completo=alumno.nombre_completo,
                matricula=alumno.matricula,
                correo=alumno.correo
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return docentes_alumnos_pb2.AlumnoProfile()
        finally:
            db.close()

    def IsAlumnoEnMateria(self, request, context):
        """Valida si un alumno pertenece a una materia (usado por MS-4/5)"""
        db = SessionLocal()
        try:
            exists = db.query(Inscripcion).filter(
                Inscripcion.alumno_id == request.alumno_id,
                Inscripcion.materia_id == request.materia_id,
                Inscripcion.activa == True
            ).first() is not None
            return docentes_alumnos_pb2.BoolResponse(exists=exists)
        except Exception as e:
            return docentes_alumnos_pb2.BoolResponse(exists=False)
        finally:
            db.close()