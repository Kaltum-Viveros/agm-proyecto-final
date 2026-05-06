from uuid import UUID

# Estructura:
# {
#   calificacion_id: {
#       "id": UUID,
#       "actividad_id": UUID,
#       "materia_id": UUID,
#       "alumno_id": UUID,
#       "calificacion": Decimal,
#       "observaciones": str | None
#   }
# }
calificaciones_store: dict[UUID, dict] = {}


class CalificacionMemoryRepository:
    def create(self, calificacion: dict) -> dict:
        calificaciones_store[calificacion["id"]] = calificacion
        return calificacion

    def get_by_id(self, calificacion_id: UUID) -> dict | None:
        return calificaciones_store.get(calificacion_id)

    def get_by_actividad(self, actividad_id: UUID) -> list[dict]:
        return [
            calificacion
            for calificacion in calificaciones_store.values()
            if calificacion["actividad_id"] == actividad_id
        ]

    def get_by_alumno_and_materia(self, alumno_id: UUID, materia_id: UUID) -> list[dict]:
        return [
            calificacion
            for calificacion in calificaciones_store.values()
            if calificacion["alumno_id"] == alumno_id
            and calificacion["materia_id"] == materia_id
        ]

    def update(self, calificacion_id: UUID, data: dict) -> dict | None:
        calificacion = calificaciones_store.get(calificacion_id)

        if calificacion is None:
            return None

        calificacion.update(data)
        calificaciones_store[calificacion_id] = calificacion

        return calificacion

    def delete(self, calificacion_id: UUID) -> bool:
        if calificacion_id not in calificaciones_store:
            return False

        del calificaciones_store[calificacion_id]
        return True

    def exists_by_actividad_and_alumno(
        self,
        actividad_id: UUID,
        alumno_id: UUID,
        exclude_calificacion_id: UUID | None = None,
    ) -> bool:
        return any(
            calificacion["actividad_id"] == actividad_id
            and calificacion["alumno_id"] == alumno_id
            and calificacion["id"] != exclude_calificacion_id
            for calificacion in calificaciones_store.values()
        )

    def exists_by_actividad_id(self, actividad_id: UUID) -> bool:
        return any(
            calificacion["actividad_id"] == actividad_id
            for calificacion in calificaciones_store.values()
        )
    
    
    def get_by_materia(self, materia_id: UUID) -> list[dict]:
        return [
            calificacion
            for calificacion in calificaciones_store.values()
            if calificacion["materia_id"] == materia_id
        ]