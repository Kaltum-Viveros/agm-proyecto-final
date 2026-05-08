import sys
from pathlib import Path
from uuid import UUID

import grpc
from fastapi import HTTPException

# Necesario porque el archivo generado calificaciones_pb2_grpc.py importa calificaciones_pb2
# como módulo directo.
generated_path = Path(__file__).resolve().parents[1] / "generated"
sys.path.append(str(generated_path))

from app.grpc.generated import calificaciones_pb2, calificaciones_pb2_grpc

from app.db.session import SessionLocal
from app.repositories.sqlalchemy.actividad_repository import ActividadRepository
from app.repositories.sqlalchemy.calificacion_repository import CalificacionRepository
from app.repositories.sqlalchemy.ponderacion_repository import PonderacionRepository
from app.services.concentrado_service import ConcentradoService


class CalificacionesGrpcService(calificaciones_pb2_grpc.CalificacionesServiceServicer):
    async def GetConcentrado(self, request, context):
        try:
            materia_id = UUID(request.materia_id)
            modo = self._normalizar_modo(request.modo)

            data = self._obtener_concentrado_data(materia_id=materia_id, modo=modo)

            return self._build_concentrado_response(data)

        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "materia_id no es un UUID válido")
        except HTTPException as exc:
            await context.abort(self._http_to_grpc_status(exc.status_code), str(exc.detail))
        except Exception as exc:
            await context.abort(grpc.StatusCode.INTERNAL, str(exc))

    async def GetPromedioAlumno(self, request, context):
        try:
            alumno_id = UUID(request.alumno_id)
            materia_id = UUID(request.materia_id)
            modo = self._normalizar_modo(request.modo)

            data = self._obtener_concentrado_data(materia_id=materia_id, modo=modo)

            alumno = next(
                (
                    item
                    for item in data["alumnos"]
                    if item["alumno_id"] == alumno_id
                ),
                None,
            )

            if alumno is None:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "No existen calificaciones para el alumno en esta materia",
                )

            return calificaciones_pb2.PromedioAlumnoResponse(
                alumno_id=str(alumno["alumno_id"]),
                materia_id=str(materia_id),
                modo=modo,
                peso_considerado=float(alumno["peso_considerado"]),
                promedio_real=float(alumno["promedio_real"]),
                promedio_redondeado=int(alumno["promedio_redondeado"]),
                detalle_ponderaciones=[
                    self._build_detalle_ponderacion(detalle)
                    for detalle in alumno["detalle_ponderaciones"]
                ],
            )

        except ValueError:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "alumno_id o materia_id no tienen formato UUID válido",
            )
        except HTTPException as exc:
            await context.abort(self._http_to_grpc_status(exc.status_code), str(exc.detail))
        except Exception as exc:
            await context.abort(grpc.StatusCode.INTERNAL, str(exc))

    async def GetEstadisticasMateria(self, request, context):
        try:
            materia_id = UUID(request.materia_id)
            modo = self._normalizar_modo(request.modo)

            data = self._obtener_concentrado_data(materia_id=materia_id, modo=modo)
            alumnos = data["alumnos"]

            if not alumnos:
                return calificaciones_pb2.StatsMateriaResponse(
                    materia_id=str(materia_id),
                    modo=modo,
                    total_alumnos=0,
                    promedio_grupal=0,
                    aprobados=0,
                    reprobados=0,
                    promedio_minimo=0,
                    promedio_maximo=0,
                )

            promedios = [float(alumno["promedio_real"]) for alumno in alumnos]
            aprobados = sum(
                1 for alumno in alumnos if int(alumno["promedio_redondeado"]) >= 6
            )
            reprobados = len(alumnos) - aprobados

            promedio_grupal = sum(promedios) / len(promedios)

            return calificaciones_pb2.StatsMateriaResponse(
                materia_id=str(materia_id),
                modo=modo,
                total_alumnos=len(alumnos),
                promedio_grupal=round(promedio_grupal, 2),
                aprobados=aprobados,
                reprobados=reprobados,
                promedio_minimo=round(min(promedios), 2),
                promedio_maximo=round(max(promedios), 2),
            )

        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "materia_id no es un UUID válido")
        except HTTPException as exc:
            await context.abort(self._http_to_grpc_status(exc.status_code), str(exc.detail))
        except Exception as exc:
            await context.abort(grpc.StatusCode.INTERNAL, str(exc))

    def _obtener_concentrado_data(self, materia_id: UUID, modo: str) -> dict:
        db = SessionLocal()

        try:
            service = ConcentradoService(
                ponderacion_repository=PonderacionRepository(db),
                actividad_repository=ActividadRepository(db),
                calificacion_repository=CalificacionRepository(db),
            )

            return service.obtener_concentrado(materia_id=materia_id, modo=modo)

        finally:
            db.close()

    def _normalizar_modo(self, modo: str) -> str:
        modo_normalizado = (modo or "actual").strip().lower()

        if modo_normalizado not in ["actual", "final"]:
            raise HTTPException(
                status_code=400,
                detail="El modo debe ser 'actual' o 'final'",
            )

        return modo_normalizado

    def _build_concentrado_response(self, data: dict):
        return calificaciones_pb2.GetConcentradoResponse(
            materia_id=str(data["materia_id"]),
            modo=data["modo"],
            total_alumnos=int(data["total_alumnos"]),
            ponderaciones=[
                calificaciones_pb2.PonderacionInfo(
                    id=str(ponderacion["id"]),
                    materia_id=str(ponderacion["materia_id"]),
                    nombre=ponderacion["nombre"],
                    porcentaje=float(ponderacion["porcentaje"]),
                    orden=int(ponderacion["orden"]),
                )
                for ponderacion in data["ponderaciones"]
            ],
            alumnos=[
                calificaciones_pb2.AlumnoConcentrado(
                    alumno_id=str(alumno["alumno_id"]),
                    modo=alumno["modo"],
                    peso_considerado=float(alumno["peso_considerado"]),
                    promedio_real=float(alumno["promedio_real"]),
                    promedio_redondeado=int(alumno["promedio_redondeado"]),
                    detalle_ponderaciones=[
                        self._build_detalle_ponderacion(detalle)
                        for detalle in alumno["detalle_ponderaciones"]
                    ],
                )
                for alumno in data["alumnos"]
            ],
        )

    def _build_detalle_ponderacion(self, detalle: dict):
        return calificaciones_pb2.DetallePonderacion(
            ponderacion_id=str(detalle["ponderacion_id"]),
            nombre=detalle["nombre"],
            porcentaje=float(detalle["porcentaje"]),
            total_actividades=int(detalle["total_actividades"]),
            actividades_calificadas=int(detalle["actividades_calificadas"]),
            promedio_criterio=float(detalle["promedio_criterio"]),
            aporte=float(detalle["aporte"]),
            incluida_en_calculo=bool(detalle["incluida_en_calculo"]),
        )

    def _http_to_grpc_status(self, http_status: int):
        if http_status == 400:
            return grpc.StatusCode.INVALID_ARGUMENT

        if http_status == 404:
            return grpc.StatusCode.NOT_FOUND

        if http_status == 409:
            return grpc.StatusCode.ALREADY_EXISTS

        return grpc.StatusCode.INTERNAL