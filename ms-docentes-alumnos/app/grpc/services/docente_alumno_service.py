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

    def GetAlumnoByEmail(self, request, context):
        """Busca perfil de alumno por correo (usado por MS-4 al importar Excel)"""
        db = SessionLocal()
        try:
            alumno = db.query(Alumno).filter(Alumno.correo == request.email.strip().lower()).first()
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

    def GetDocenteByNombre(self, request, context):
        """
        Busca un docente por nombre (usado por MS-2 al importar PDF de programación).
        Hace una búsqueda flexible: verifica si todas las palabras del nombre
        del PDF están contenidas en el nombre completo registrado.
        """
        import unicodedata

        def normalizar(t: str) -> str:
            if not t:
                return ""
            t = unicodedata.normalize('NFD', t).encode('ascii', 'ignore').decode('utf-8')
            return t.upper().strip()

        db = SessionLocal()
        try:
            nombre_buscado = normalizar(request.nombre_completo)
            palabras_buscadas = set(nombre_buscado.split())

            todos_docentes = db.query(Docente).filter(Docente.estatus_laboral == True).all()

            for docente in todos_docentes:
                nombre_db = normalizar(docente.nombre_completo)
                palabras_db = set(nombre_db.split())
                # Coincide si las palabras del PDF están todas en el nombre registrado
                if palabras_buscadas.issubset(palabras_db):
                    return docentes_alumnos_pb2.DocenteProfile(
                        docente_id=str(docente.docente_id),
                        nombre_completo=docente.nombre_completo,
                        correo=docente.correo,
                        encontrado=True
                    )

            # No encontrado — retornar con encontrado=False en lugar de lanzar error
            return docentes_alumnos_pb2.DocenteProfile(encontrado=False)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return docentes_alumnos_pb2.DocenteProfile(encontrado=False)
        finally:
            db.close()

    def GetDocenteByEmail(self, request, context):
        """Busca un docente por su correo electrónico"""
        db = SessionLocal()
        try:
            docente = db.query(Docente).filter(Docente.correo == request.email.strip().lower()).first()
            if not docente:
                return docentes_alumnos_pb2.DocenteProfile(encontrado=False)
            
            return docentes_alumnos_pb2.DocenteProfile(
                docente_id=str(docente.docente_id),
                nombre_completo=docente.nombre_completo,
                correo=docente.correo,
                encontrado=True
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return docentes_alumnos_pb2.DocenteProfile(encontrado=False)
        finally:
            db.close()