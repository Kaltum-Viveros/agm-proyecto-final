from uuid import UUID

# Estructura:
# {
#   actividad_id: {
#       "id": UUID,
#       "materia_id": UUID,
#       "ponderacion_id": UUID,
#       "nombre": str,
#       "descripcion": str | None,
#       "valor_maximo": Decimal,
#       "fecha_aplicacion": date | None,
#       "estado": str
#   }
# }
actividades_store: dict[UUID, dict] = {}


class ActividadMemoryRepository:
    def create(self, actividad: dict) -> dict:
        actividades_store[actividad["id"]] = actividad
        return actividad

    def get_by_id(self, actividad_id: UUID) -> dict | None:
        return actividades_store.get(actividad_id)

    def get_by_materia(self, materia_id: UUID) -> list[dict]:
        return [
            actividad
            for actividad in actividades_store.values()
            if actividad["materia_id"] == materia_id
        ]

    def update(self, actividad_id: UUID, data: dict) -> dict | None:
        actividad = actividades_store.get(actividad_id)

        if actividad is None:
            return None

        actividad.update(data)
        actividades_store[actividad_id] = actividad

        return actividad

    def delete(self, actividad_id: UUID) -> bool:
        if actividad_id not in actividades_store:
            return False

        del actividades_store[actividad_id]
        return True

    def exists_by_ponderacion_ids(self, ponderacion_ids: list[UUID]) -> bool:
        ponderacion_ids_set = set(ponderacion_ids)

        return any(
            actividad["ponderacion_id"] in ponderacion_ids_set
            for actividad in actividades_store.values()
        )

    def exists_by_ponderacion_and_nombre(
        self,
        ponderacion_id: UUID,
        nombre: str,
        exclude_actividad_id: UUID | None = None,
    ) -> bool:
        nombre_normalizado = nombre.lower().strip()

        return any(
            actividad["ponderacion_id"] == ponderacion_id
            and actividad["nombre"].lower().strip() == nombre_normalizado
            and actividad["id"] != exclude_actividad_id
            for actividad in actividades_store.values()
        )