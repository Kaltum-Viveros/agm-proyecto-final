from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.grpc.clients.alumnos_client import AlumnosGrpcClient
from app.repositories.actividad_memory_repository import ActividadMemoryRepository
from app.repositories.calificacion_memory_repository import CalificacionMemoryRepository
from app.schemas.calificacion import CalificacionCreate, CalificacionUpdate


class CalificacionService:
    def __init__(
        self,
        calificacion_repository: CalificacionMemoryRepository,
        actividad_repository: ActividadMemoryRepository,
    ):
        self.calificacion_repository = calificacion_repository
        self.actividad_repository = actividad_repository

    def crear(self, payload: CalificacionCreate) -> dict:
        actividad = self.actividad_repository.get_by_id(payload.actividad_id)

        if actividad is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Actividad no encontrada",
            )

        if actividad["estado"] == "cerrada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden registrar calificaciones en una actividad cerrada",
            )

        if payload.calificacion > actividad["valor_maximo"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La calificación no puede superar el valor máximo de la actividad ({actividad['valor_maximo']})",
            )

        if self.calificacion_repository.exists_by_actividad_and_alumno(
            actividad_id=payload.actividad_id,
            alumno_id=payload.alumno_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El alumno ya tiene una calificación registrada para esta actividad",
            )

        # TODO: Conectar con cliente gRPC del MS-3 (Docentes & Alumnos) para validar que el alumno exista
        # y que esté inscrito en la materia (actividad["materia_id"]).
        # Ejemplo simulado de validación exitosa:
        alumno_valido = True # Simulación
        if not alumno_valido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El alumno no existe o no está inscrito en la materia",
            )

        calificacion = {
            "id": uuid4(),
            "actividad_id": payload.actividad_id,
            "materia_id": actividad["materia_id"],
            "alumno_id": payload.alumno_id,
            "calificacion": payload.calificacion,
            "observaciones": payload.observaciones,
            "actividad_nombre": actividad["nombre"],
        }

        return self.calificacion_repository.create(calificacion)

    def obtener_por_id(self, calificacion_id: UUID) -> dict:
        calificacion = self.calificacion_repository.get_by_id(calificacion_id)

        if calificacion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calificación no encontrada",
            )

        return calificacion

    def obtener_por_actividad(self, actividad_id: UUID) -> list[dict]:
        actividad = self.actividad_repository.get_by_id(actividad_id)

        if actividad is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Actividad no encontrada",
            )

        return self.calificacion_repository.get_by_actividad(actividad_id)

    def obtener_por_alumno_y_materia(self, alumno_id: UUID, materia_id: UUID) -> list[dict]:
        return self.calificacion_repository.get_by_alumno_and_materia(
            alumno_id=alumno_id,
            materia_id=materia_id,
        )

    def actualizar(self, calificacion_id: UUID, payload: CalificacionUpdate) -> dict:
        calificacion_actual = self.obtener_por_id(calificacion_id)
        actividad = self.actividad_repository.get_by_id(calificacion_actual["actividad_id"])

        if actividad is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Actividad asociada no encontrada",
            )

        if actividad["estado"] == "cerrada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede modificar una calificación de una actividad cerrada",
            )

        update_data = payload.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos para actualizar",
            )

        if "calificacion" in update_data and update_data["calificacion"] > actividad["valor_maximo"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La calificación no puede superar el valor máximo de la actividad ({actividad['valor_maximo']})",
            )

        calificacion_actualizada = self.calificacion_repository.update(
            calificacion_id=calificacion_id,
            data=update_data,
        )

        if calificacion_actualizada is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calificación no encontrada",
            )

        return calificacion_actualizada

    def eliminar(self, calificacion_id: UUID) -> None:
        calificacion = self.obtener_por_id(calificacion_id)
        actividad = self.actividad_repository.get_by_id(calificacion["actividad_id"])

        if actividad and actividad["estado"] == "cerrada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una calificación de una actividad cerrada",
            )

        deleted = self.calificacion_repository.delete(calificacion_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calificación no encontrada",
            )