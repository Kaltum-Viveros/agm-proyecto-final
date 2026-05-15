from uuid import UUID

import grpc
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.periodo import Periodo
from app.models.materia_catalogo import MateriaCatalogo
from app.models.materia_ofertada import MateriaOfertada
from app.models.materia_horario import MateriaHorario
from app.grpc.generated import periodos_materias_pb2
from app.grpc.generated import periodos_materias_pb2_grpc


def _to_str(value) -> str:
    return "" if value is None else str(value)


def _date_to_str(value) -> str:
    return "" if value is None else value.isoformat()


def _time_to_str(value) -> str:
    return "" if value is None else value.isoformat()


def _parse_uuid(value: str):
    if not value:
        raise ValueError("UUID vacío")

    return UUID(value)


class PeriodosMateriasGrpcService(
    periodos_materias_pb2_grpc.PeriodosMateriasServiceServicer
):
    async def GetMateriaById(self, request, context):
        try:
            materia_id = _parse_uuid(request.materia_id)
        except ValueError:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "materia_id no es un UUID válido"
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MateriaOfertada)
                .where(MateriaOfertada.materia_ofertada_id == materia_id)
            )
            materia_ofertada = result.scalar_one_or_none()

            if materia_ofertada is None:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Materia ofertada no encontrada"
                )

            return await self._build_materia_info(db, materia_ofertada)

    async def GetMateriasByDocente(self, request, context):
        try:
            docente_id = _parse_uuid(request.docente_id)
        except ValueError:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "docente_id no es un UUID válido"
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MateriaOfertada)
                .where(MateriaOfertada.docente_id == docente_id)
                .order_by(MateriaOfertada.nrc.asc())
            )
            materias_ofertadas = result.scalars().all()

            materias = [
                await self._build_materia_info(db, materia_ofertada)
                for materia_ofertada in materias_ofertadas
            ]

            return periodos_materias_pb2.MateriasDocenteResponse(
                materias=materias
            )

    async def GetMateriaByNRC(self, request, context):
        """Busca una materia por su NRC (global)"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MateriaOfertada)
                .where(MateriaOfertada.nrc == request.nrc)
                .limit(1)
            )
            materia_ofertada = result.scalar_one_or_none()

            if materia_ofertada is None:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"Materia con NRC {request.nrc} no encontrada"
                )

            return await self._build_materia_info(db, materia_ofertada)

    async def GetPeriodoActivo(self, request, context):
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Periodo)
                .where(Periodo.activo.is_(True))
                .limit(1)
            )
            periodo = result.scalar_one_or_none()

            if periodo is None:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "No existe periodo activo"
                )

            return self._build_periodo_info(periodo)

    async def _build_materia_info(self, db, materia_ofertada: MateriaOfertada):
        periodo = await db.get(Periodo, materia_ofertada.periodo_id)
        materia_catalogo = await db.get(
            MateriaCatalogo,
            materia_ofertada.materia_catalogo_id
        )

        result_horarios = await db.execute(
            select(MateriaHorario)
            .where(
                MateriaHorario.materia_ofertada_id
                == materia_ofertada.materia_ofertada_id
            )
            .order_by(
                MateriaHorario.dia.asc(),
                MateriaHorario.hora_inicio.asc()
            )
        )
        horarios = result_horarios.scalars().all()

        return periodos_materias_pb2.MateriaInfo(
            materia_ofertada_id=_to_str(materia_ofertada.materia_ofertada_id),
            nrc=_to_str(materia_ofertada.nrc),
            seccion=_to_str(materia_ofertada.seccion),
            estado=_to_str(materia_ofertada.estado),
            periodo=self._build_periodo_info(periodo),
            materia=self._build_materia_catalogo_info(materia_catalogo),
            docente_id=_to_str(materia_ofertada.docente_id),
            docente_nombre=_to_str(materia_ofertada.docente_nombre),
            horarios=[
                periodos_materias_pb2.HorarioInfo(
                    materia_horario_id=_to_str(horario.materia_horario_id),
                    dia=_to_str(horario.dia),
                    hora_inicio=_time_to_str(horario.hora_inicio),
                    hora_fin=_time_to_str(horario.hora_fin),
                    salon=_to_str(horario.salon),
                )
                for horario in horarios
            ],
        )

    def _build_periodo_info(self, periodo: Periodo):
        if periodo is None:
            return periodos_materias_pb2.PeriodoInfo()

        return periodos_materias_pb2.PeriodoInfo(
            periodo_id=_to_str(periodo.periodo_id),
            nombre=_to_str(periodo.nombre),
            fecha_inicio=_date_to_str(periodo.fecha_inicio),
            fecha_fin=_date_to_str(periodo.fecha_fin),
            activo=bool(periodo.activo),
        )

    def _build_materia_catalogo_info(self, materia_catalogo: MateriaCatalogo):
        if materia_catalogo is None:
            return periodos_materias_pb2.MateriaCatalogoInfo()

        return periodos_materias_pb2.MateriaCatalogoInfo(
            materia_catalogo_id=_to_str(
                materia_catalogo.materia_catalogo_id
            ),
            clave=_to_str(materia_catalogo.clave),
            nombre=_to_str(materia_catalogo.nombre),
        )