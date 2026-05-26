from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.materia_catalogo import MateriaCatalogo
from app.models.materia_horario import MateriaHorario
from app.models.materia_ofertada import MateriaOfertada
from app.models.materia_plan_estudio import MateriaPlanEstudio
from app.models.periodo import Periodo
from app.models.plan_estudio import PlanEstudio
from app.utils.pdf_programacion_parser import ProgramacionAcademicaRow
from app.core.academic_rules import validar_rango_horas
from app.messaging.clients.docentes_hybrid_client import docentes_client


class ImportacionProgramacionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def importar_programacion(
        self,
        periodo_id: UUID,
        plan_estudio_id: UUID,
        rows: list[ProgramacionAcademicaRow],
        archivo: str,
        advertencias: list[str],
    ) -> dict:
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No se pudieron extraer filas válidas del PDF.",
            )

        periodo = await self.db.get(Periodo, periodo_id)

        if not periodo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El periodo indicado no existe.",
            )

        plan_estudio = await self.db.get(PlanEstudio, plan_estudio_id)

        if not plan_estudio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El plan de estudio indicado no existe.",
            )

        grouped_rows = self._group_rows_by_oferta(rows)

        materias_creadas = 0
        relaciones_plan_creadas = 0
        ofertas_creadas = 0
        ofertas_actualizadas = 0
        horarios_creados = 0

        try:
            for group in grouped_rows.values():
                base_row = group["base"]
                horarios = group["horarios"]

                materia, materia_created = await self._get_or_create_materia_catalogo(base_row)

                if materia_created:
                    materias_creadas += 1

                relacion_created = await self._ensure_materia_plan_estudio(
                    materia_catalogo_id=materia.materia_catalogo_id,
                    plan_estudio_id=plan_estudio_id,
                )

                if relacion_created:
                    relaciones_plan_creadas += 1

                oferta, oferta_created = await self._get_or_create_materia_ofertada(
                    periodo_id=periodo_id,
                    materia_catalogo_id=materia.materia_catalogo_id,
                    base_row=base_row,
                )

                if oferta_created:
                    ofertas_creadas += 1
                else:
                    ofertas_actualizadas += 1

                await self._replace_horarios(
                    materia_ofertada_id=oferta.materia_ofertada_id,
                    horarios=horarios,
                )

                horarios_creados += len(self._unique_horarios(horarios))

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return {
            "archivo": archivo,
            "filas_extraidas": len(rows),
            "ofertas_procesadas": len(grouped_rows),
            "materias_creadas": materias_creadas,
            "relaciones_plan_creadas": relaciones_plan_creadas,
            "ofertas_creadas": ofertas_creadas,
            "ofertas_actualizadas": ofertas_actualizadas,
            "horarios_creados": horarios_creados,
            "advertencias": advertencias,
        }

    def _group_rows_by_oferta(
        self,
        rows: list[ProgramacionAcademicaRow],
    ) -> dict[tuple[str, str, str], dict]:
        grouped: dict[tuple[str, str, str], dict] = {}

        for row in rows:
            key = (row.nrc, row.clave, row.seccion)

            if key not in grouped:
                grouped[key] = {
                    "base": row,
                    "horarios": [],
                }

            grouped[key]["horarios"].append(row)

        return grouped

    async def _get_or_create_materia_catalogo(
        self,
        row: ProgramacionAcademicaRow,
    ) -> tuple[MateriaCatalogo, bool]:
        statement = select(MateriaCatalogo).where(MateriaCatalogo.clave == row.clave)

        result = await self.db.execute(statement)
        materia = result.scalar_one_or_none()

        if materia:
            return materia, False

        materia = MateriaCatalogo(
            clave=row.clave,
            nombre=row.materia,
            activo=True,
        )

        self.db.add(materia)
        await self.db.flush()

        return materia, True

    async def _ensure_materia_plan_estudio(
        self,
        materia_catalogo_id: UUID,
        plan_estudio_id: UUID,
    ) -> bool:
        statement = select(MateriaPlanEstudio).where(
            MateriaPlanEstudio.materia_catalogo_id == materia_catalogo_id,
            MateriaPlanEstudio.plan_estudio_id == plan_estudio_id,
        )

        result = await self.db.execute(statement)
        relation = result.scalar_one_or_none()

        if relation:
            if not relation.activa:
                relation.activa = True
                await self.db.flush()

            return False

        relation = MateriaPlanEstudio(
            materia_catalogo_id=materia_catalogo_id,
            plan_estudio_id=plan_estudio_id,
            activa=True,
        )

        self.db.add(relation)
        await self.db.flush()

        return True

    async def _get_or_create_materia_ofertada(
        self,
        periodo_id: UUID,
        materia_catalogo_id: UUID,
        base_row: ProgramacionAcademicaRow,
    ) -> tuple[MateriaOfertada, bool]:
        # Intentar resolver el docente_id vía gRPC a MS-3 (no bloquea si falla)
        docente_id_resuelto = None
        if base_row.profesor:
            try:
                docente_id_str = await docentes_client.resolver_docente_por_nombre_async(base_row.profesor)
                if docente_id_str:
                    from uuid import UUID as _UUID
                    docente_id_resuelto = _UUID(docente_id_str)
            except Exception:
                pass  # Fallo silencioso: el nombre igual se guarda

        statement = select(MateriaOfertada).where(
            MateriaOfertada.periodo_id == periodo_id,
            MateriaOfertada.nrc == base_row.nrc,
            MateriaOfertada.seccion == base_row.seccion,
        )

        result = await self.db.execute(statement)
        oferta = result.scalar_one_or_none()

        if oferta:
            oferta.materia_catalogo_id = materia_catalogo_id
            oferta.docente_id = docente_id_resuelto
            oferta.docente_nombre = base_row.profesor
            oferta.estado = "ACTIVA"

            await self.db.flush()

            return oferta, False

        oferta = MateriaOfertada(
            periodo_id=periodo_id,
            materia_catalogo_id=materia_catalogo_id,
            nrc=base_row.nrc,
            seccion=base_row.seccion,
            docente_id=docente_id_resuelto,
            docente_nombre=base_row.profesor,
            estado="ACTIVA",
        )

        self.db.add(oferta)
        await self.db.flush()

        return oferta, True

    async def _replace_horarios(
        self,
        materia_ofertada_id: UUID,
        horarios: list[ProgramacionAcademicaRow],
    ) -> None:
        await self.db.execute(
            delete(MateriaHorario).where(
                MateriaHorario.materia_ofertada_id == materia_ofertada_id
            )
        )

        unique_horarios = self._unique_horarios(horarios)

        for row in unique_horarios:
            validar_rango_horas(row.hora_inicio, row.hora_fin)

            horario = MateriaHorario(
                materia_ofertada_id=materia_ofertada_id,
                dia=row.dia,
                hora_inicio=row.hora_inicio,
                hora_fin=row.hora_fin,
                salon=row.salon,
            )

            self.db.add(horario)

        await self.db.flush()

    def _unique_horarios(
        self,
        horarios: list[ProgramacionAcademicaRow],
    ) -> list[ProgramacionAcademicaRow]:
        seen: set[tuple] = set()
        unique: list[ProgramacionAcademicaRow] = []

        for row in horarios:
            key = (row.dia, row.hora_inicio, row.hora_fin, row.salon)

            if key in seen:
                continue

            seen.add(key)
            unique.append(row)

        return unique
