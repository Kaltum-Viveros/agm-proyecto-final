from decimal import Decimal, InvalidOperation
from io import BytesIO
from uuid import UUID, NAMESPACE_DNS, uuid4, uuid5

import pandas as pd
from fastapi import HTTPException, UploadFile, status

from app.repositories.actividad_memory_repository import ActividadMemoryRepository
from app.repositories.calificacion_memory_repository import CalificacionMemoryRepository


class ImportacionCalificacionesService:
    def __init__(
        self,
        calificacion_repository: CalificacionMemoryRepository,
        actividad_repository: ActividadMemoryRepository,
    ):
        self.calificacion_repository = calificacion_repository
        self.actividad_repository = actividad_repository

    async def importar_excel(
        self,
        actividad_id: UUID,
        archivo: UploadFile,
        columna_correo: str = "Dirección de correo",
        columna_puntos: str = "Puntos",
        columna_puntos_maximos: str = "Puntos máximos",
        columna_observaciones: str = "Comentarios",
    ) -> dict:
        actividad = self.actividad_repository.get_by_id(actividad_id)

        if actividad is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Actividad no encontrada",
            )

        if actividad["estado"] == "cerrada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden importar calificaciones en una actividad cerrada",
            )

        df = await self._leer_archivo(archivo)

        self._validar_columnas(
            df=df,
            columnas_requeridas=[
                columna_correo,
                columna_puntos,
                columna_puntos_maximos,
            ],
        )

        procesadas = 0
        insertadas = 0
        actualizadas = 0
        omitidas: list[dict] = []
        errores: list[dict] = []

        for index, row in df.iterrows():
            numero_fila_excel = int(index) + 2
            procesadas += 1

            try:
                correo = self._obtener_texto(row.get(columna_correo))

                if not correo:
                    raise ValueError("Correo del alumno vacío")

                valor_puntos = row.get(columna_puntos)
                valor_puntos_maximos = row.get(columna_puntos_maximos)

                if self._valor_vacio(valor_puntos):
                    omitidas.append(
                        {
                            "fila": numero_fila_excel,
                            "motivo": "Fila sin puntos; se considera no calificada",
                            "correo": correo,
                        }
                    )
                    continue

                if self._valor_vacio(valor_puntos_maximos):
                    raise ValueError("Puntos máximos vacío; no se puede calcular la calificación")

                puntos = self._decimal_desde_excel(valor_puntos)
                puntos_maximos = self._decimal_desde_excel(valor_puntos_maximos)

                if puntos_maximos <= 0:
                    raise ValueError("Puntos máximos debe ser mayor a 0")

                if puntos < 0:
                    raise ValueError("Puntos no puede ser negativo")

                if puntos > puntos_maximos:
                    raise ValueError("Puntos no puede ser mayor que puntos máximos")

                alumno_id = self._generar_alumno_id_mock(correo)

                calificacion_calculada = (
                    puntos / puntos_maximos
                ) * Decimal(str(actividad["valor_maximo"]))

                calificacion_calculada = calificacion_calculada.quantize(Decimal("0.01"))

                observaciones = None
                if columna_observaciones in df.columns:
                    observaciones = self._obtener_texto(row.get(columna_observaciones)) or None

                calificacion_existente = self.calificacion_repository.get_by_actividad_and_alumno(
                    actividad_id=actividad_id,
                    alumno_id=alumno_id,
                )

                if calificacion_existente:
                    self.calificacion_repository.update(
                        calificacion_id=calificacion_existente["id"],
                        data={
                            "calificacion": calificacion_calculada,
                            "observaciones": observaciones,
                            "alumno_referencia": correo,
                        },
                    )
                    actualizadas += 1
                else:
                    self.calificacion_repository.create(
                        {
                            "id": uuid4(),
                            "actividad_id": actividad_id,
                            "materia_id": actividad["materia_id"],
                            "alumno_id": alumno_id,
                            "alumno_referencia": correo,
                            "calificacion": calificacion_calculada,
                            "observaciones": observaciones,
                            "actividad_nombre": actividad["nombre"],
                        }
                    )
                    insertadas += 1

            except Exception as exc:
                errores.append(
                    {
                        "fila": numero_fila_excel,
                        "motivo": str(exc),
                    }
                )

        return {
            "archivo": archivo.filename,
            "actividad_id": actividad_id,
            "materia_id": actividad["materia_id"],
            "procesadas": procesadas,
            "insertadas": insertadas,
            "actualizadas": actualizadas,
            "omitidas": omitidas,
            "errores": errores,
        }

    async def _leer_archivo(self, archivo: UploadFile) -> pd.DataFrame:
        contenido = await archivo.read()
        nombre = archivo.filename or ""

        if nombre.endswith(".xlsx") or nombre.endswith(".xls"):
            df_raw = pd.read_excel(BytesIO(contenido), sheet_name=0, header=None)
            return self._detectar_encabezados_y_limpiar(df_raw)

        if nombre.endswith(".csv"):
            df_raw = pd.read_csv(BytesIO(contenido), header=None)
            return self._detectar_encabezados_y_limpiar(df_raw)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no soportado. Usa .xlsx, .xls o .csv",
        )
    
    def _detectar_encabezados_y_limpiar(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        columnas_requeridas = {
            "Dirección de correo",
            "Puntos",
            "Puntos máximos",
        }

        header_index = None

        for index, row in df_raw.iterrows():
            valores_fila = {
                str(value).strip()
                for value in row.tolist()
                if not pd.isna(value)
            }

            if columnas_requeridas.issubset(valores_fila):
                header_index = index
                break

        if header_index is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "No se encontró la fila de encabezados en el archivo",
                    "columnas_requeridas": list(columnas_requeridas),
                },
            )

        columnas = [
            str(value).strip() if not pd.isna(value) else f"Unnamed_{i}"
            for i, value in enumerate(df_raw.iloc[header_index].tolist())
        ]

        df = df_raw.iloc[header_index + 1:].copy()
        df.columns = columnas

        # Elimina columnas completamente vacías.
        df = df.dropna(axis=1, how="all")

        # Elimina filas completamente vacías.
        df = df.dropna(axis=0, how="all")

        # Limpia espacios en nombres de columnas.
        df.columns = [str(col).strip() for col in df.columns]

        return df

    def _validar_columnas(self, df: pd.DataFrame, columnas_requeridas: list[str]) -> None:
        columnas_faltantes = [
            columna for columna in columnas_requeridas if columna not in df.columns
        ]

        if columnas_faltantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "El archivo no contiene las columnas requeridas",
                    "columnas_faltantes": columnas_faltantes,
                    "columnas_detectadas": list(df.columns),
                },
            )

    def _obtener_texto(self, value) -> str:
        if pd.isna(value):
            return ""

        return str(value).strip()
    
    def _valor_vacio(self, value) -> bool:
        if pd.isna(value):
            return True

        return str(value).strip() == ""
    

    def _decimal_desde_excel(self, value) -> Decimal:
        if pd.isna(value):
            raise ValueError("Valor numérico vacío")

        try:
            return Decimal(str(value).replace(",", ".").strip())
        except (InvalidOperation, AttributeError):
            raise ValueError(f"Valor numérico inválido: {value}")

    def _generar_alumno_id_mock(self, correo: str) -> UUID:
        return uuid5(NAMESPACE_DNS, correo.lower().strip())