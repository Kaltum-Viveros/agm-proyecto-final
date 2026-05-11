import os
import shutil
import tempfile
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.importacion_pdf import ImportacionProgramacionResponse
from app.services.importacion_pdf_service import ImportacionProgramacionService
from app.utils.pdf_programacion_parser import parse_programacion_academica_pdf

router = APIRouter()


@router.post(
    "/programacion-academica",
    response_model=ImportacionProgramacionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def importar_programacion_academica(
    periodo_id: UUID = Form(...),
    plan_estudio_id: UUID = Form(...),
    archivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not archivo.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes subir un archivo PDF.",
        )

    if not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un PDF.",
        )

    temp_path = ""

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_path = temp_file.name
            shutil.copyfileobj(archivo.file, temp_file)

        parse_result = parse_programacion_academica_pdf(temp_path)

        service = ImportacionProgramacionService(db)

        return await service.importar_programacion(
            periodo_id=periodo_id,
            plan_estudio_id=plan_estudio_id,
            rows=parse_result.rows,
            archivo=archivo.filename,
            advertencias=parse_result.warnings,
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)