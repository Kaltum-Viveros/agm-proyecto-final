from pydantic import BaseModel


class ImportacionProgramacionResponse(BaseModel):
    archivo: str
    filas_extraidas: int
    ofertas_procesadas: int
    materias_creadas: int
    relaciones_plan_creadas: int
    ofertas_creadas: int
    ofertas_actualizadas: int
    horarios_creados: int
    advertencias: list[str] = []