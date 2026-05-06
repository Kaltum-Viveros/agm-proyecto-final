from app.models.materia_catalogo import MateriaCatalogo
from app.models.materia_horario import MateriaHorario
from app.models.materia_ofertada import MateriaOfertada
from app.models.materia_plan_estudio import MateriaPlanEstudio
from app.models.periodo import Periodo
from app.models.plan_estudio import PlanEstudio

__all__ = [
    "Periodo",
    "PlanEstudio",
    "MateriaCatalogo",
    "MateriaPlanEstudio",
    "MateriaOfertada",
    "MateriaHorario",
]