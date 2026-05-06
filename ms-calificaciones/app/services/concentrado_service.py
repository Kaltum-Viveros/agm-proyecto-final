from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status

from app.repositories.actividad_memory_repository import ActividadMemoryRepository
from app.repositories.calificacion_memory_repository import CalificacionMemoryRepository
from app.repositories.ponderacion_memory_repository import PonderacionMemoryRepository
from app.utils.rounding import redondear_promedio


class ConcentradoService:
    def __init__(
        self,
        ponderacion_repository: PonderacionMemoryRepository,
        actividad_repository: ActividadMemoryRepository,
        calificacion_repository: CalificacionMemoryRepository,
    ):
        self.ponderacion_repository = ponderacion_repository
        self.actividad_repository = actividad_repository
        self.calificacion_repository = calificacion_repository

    def obtener_concentrado(self, materia_id: UUID) -> dict:
        ponderaciones = self.ponderacion_repository.get_by_materia(materia_id)

        if not ponderaciones:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existen ponderaciones configuradas para esta materia",
            )

        actividades = self.actividad_repository.get_by_materia(materia_id)
        calificaciones = self.calificacion_repository.get_by_materia(materia_id)

        alumnos_ids = sorted(
            {calificacion["alumno_id"] for calificacion in calificaciones},
            key=lambda alumno_id: str(alumno_id),
        )

        calificaciones_por_alumno_actividad = {
            (calificacion["alumno_id"], calificacion["actividad_id"]): calificacion
            for calificacion in calificaciones
        }

        actividades_por_ponderacion = defaultdict(list)

        for actividad in actividades:
            actividades_por_ponderacion[actividad["ponderacion_id"]].append(actividad)

        alumnos_resultado = []

        for alumno_id in alumnos_ids:
            detalle_ponderaciones = []
            promedio_real = Decimal("0")

            for ponderacion in sorted(ponderaciones, key=lambda item: item["orden"]):
                ponderacion_id = ponderacion["id"]
                porcentaje = Decimal(str(ponderacion["porcentaje"]))
                actividades_de_ponderacion = actividades_por_ponderacion.get(ponderacion_id, [])

                promedio_criterio = self._calcular_promedio_criterio(
                    alumno_id=alumno_id,
                    actividades=actividades_de_ponderacion,
                    calificaciones_por_alumno_actividad=calificaciones_por_alumno_actividad,
                )

                aporte = promedio_criterio * (porcentaje / Decimal("100"))
                promedio_real += aporte

                detalle_ponderaciones.append(
                    {
                        "ponderacion_id": ponderacion_id,
                        "nombre": ponderacion["nombre"],
                        "porcentaje": porcentaje,
                        "promedio_criterio": round(promedio_criterio, 2),
                        "aporte": round(aporte, 2),
                    }
                )

            promedio_real = round(promedio_real, 2)
            promedio_redondeado = redondear_promedio(promedio_real)

            alumnos_resultado.append(
                {
                    "alumno_id": alumno_id,
                    "promedio_real": promedio_real,
                    "promedio_redondeado": promedio_redondeado,
                    "detalle_ponderaciones": detalle_ponderaciones,
                }
            )

        return {
            "materia_id": materia_id,
            "total_alumnos": len(alumnos_resultado),
            "ponderaciones": ponderaciones,
            "alumnos": alumnos_resultado,
        }

    def _calcular_promedio_criterio(
        self,
        alumno_id: UUID,
        actividades: list[dict],
        calificaciones_por_alumno_actividad: dict,
    ) -> Decimal:
        if not actividades:
            return Decimal("0")

        suma = Decimal("0")

        for actividad in actividades:
            calificacion = calificaciones_por_alumno_actividad.get(
                (alumno_id, actividad["id"])
            )

            if calificacion is None:
                # En este mock, actividad sin calificación cuenta como 0.
                suma += Decimal("0")
            else:
                suma += Decimal(str(calificacion["calificacion"]))

        return suma / Decimal(len(actividades))