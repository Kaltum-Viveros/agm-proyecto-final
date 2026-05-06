from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.repositories.actividad_memory_repository import ActividadMemoryRepository
from app.repositories.ponderacion_memory_repository import PonderacionMemoryRepository
from app.schemas.actividad import ActividadCreate, ActividadUpdate


class ActividadService:
    def __init__(
        self,
        actividad_repository: ActividadMemoryRepository,
        ponderacion_repository: PonderacionMemoryRepository,
    ):
        self.actividad_repository = actividad_repository
        self.ponderacion_repository = ponderacion_repository

    def crear(self, payload: ActividadCreate) -> dict:
        ponderacion = self._obtener_ponderacion_de_materia(
            materia_id=payload.materia_id,
            ponderacion_id=payload.ponderacion_id,
        )

        if self.actividad_repository.exists_by_ponderacion_and_nombre(
            ponderacion_id=payload.ponderacion_id,
            nombre=payload.nombre,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una actividad con ese nombre dentro de la ponderación",
            )

        actividad = {
            "id": uuid4(),
            "materia_id": payload.materia_id,
            "ponderacion_id": payload.ponderacion_id,
            "nombre": payload.nombre,
            "descripcion": payload.descripcion,
            "valor_maximo": payload.valor_maximo,
            "fecha_aplicacion": payload.fecha_aplicacion,
            "estado": "activa",
            "ponderacion_nombre": ponderacion["nombre"],
        }

        return self.actividad_repository.create(actividad)

    def obtener_por_id(self, actividad_id: UUID) -> dict:
        actividad = self.actividad_repository.get_by_id(actividad_id)

        if actividad is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Actividad no encontrada",
            )

        return actividad

    def obtener_por_materia(self, materia_id: UUID) -> list[dict]:
        actividades = self.actividad_repository.get_by_materia(materia_id)

        return sorted(
            actividades,
            key=lambda actividad: (
                actividad.get("fecha_aplicacion") is None,
                actividad.get("fecha_aplicacion"),
                actividad["nombre"],
            ),
        )

    def actualizar(self, actividad_id: UUID, payload: ActividadUpdate) -> dict:
        actividad_actual = self.obtener_por_id(actividad_id)

        update_data = payload.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos para actualizar",
            )

        nueva_ponderacion_id = update_data.get(
            "ponderacion_id",
            actividad_actual["ponderacion_id"],
        )

        # Si cambia la ponderación, validamos que pertenezca a la misma materia.
        if "ponderacion_id" in update_data:
            ponderacion = self._obtener_ponderacion_de_materia(
                materia_id=actividad_actual["materia_id"],
                ponderacion_id=nueva_ponderacion_id,
            )
            update_data["ponderacion_nombre"] = ponderacion["nombre"]

        nuevo_nombre = update_data.get("nombre", actividad_actual["nombre"])

        if self.actividad_repository.exists_by_ponderacion_and_nombre(
            ponderacion_id=nueva_ponderacion_id,
            nombre=nuevo_nombre,
            exclude_actividad_id=actividad_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una actividad con ese nombre dentro de la ponderación",
            )

        actividad_actualizada = self.actividad_repository.update(
            actividad_id=actividad_id,
            data=update_data,
        )

        if actividad_actualizada is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Actividad no encontrada",
            )

        return actividad_actualizada

    def eliminar(self, actividad_id: UUID) -> None:
        actividad = self.obtener_por_id(actividad_id)

        if actividad["estado"] == "cerrada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una actividad cerrada",
            )

        deleted = self.actividad_repository.delete(actividad_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Actividad no encontrada",
            )

    def _obtener_ponderacion_de_materia(self, materia_id: UUID, ponderacion_id: UUID) -> dict:
        ponderaciones = self.ponderacion_repository.get_by_materia(materia_id)

        if not ponderaciones:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existen ponderaciones configuradas para esta materia",
            )

        for ponderacion in ponderaciones:
            if ponderacion["id"] == ponderacion_id:
                return ponderacion

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La ponderación no pertenece a la materia indicada",
        )