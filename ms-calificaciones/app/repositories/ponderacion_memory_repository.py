from uuid import UUID

# Estructura:
# {
#   materia_id: [
#       {
#           "id": UUID,
#           "materia_id": UUID,
#           "nombre": str,
#           "porcentaje": Decimal,
#           "orden": int
#       }
#   ]
# }
ponderaciones_store: dict[UUID, list[dict]] = {}


class PonderacionMemoryRepository:
    def get_by_materia(self, materia_id: UUID) -> list[dict]:
        return ponderaciones_store.get(materia_id, [])

    def replace_by_materia(self, materia_id: UUID, criterios: list[dict]) -> list[dict]:
        ponderaciones_store[materia_id] = criterios
        return criterios

    def exists_for_materia(self, materia_id: UUID) -> bool:
        return materia_id in ponderaciones_store

    def delete_by_materia(self, materia_id: UUID) -> bool:
        if materia_id not in ponderaciones_store:
            return False

        del ponderaciones_store[materia_id]
        return True

    def get_ids_by_materia(self, materia_id: UUID) -> list[UUID]:
        return [
            ponderacion["id"]
            for ponderacion in ponderaciones_store.get(materia_id, [])
        ]