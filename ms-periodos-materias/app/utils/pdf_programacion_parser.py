import re
from dataclasses import dataclass
from datetime import time

import pdfplumber


@dataclass(frozen=True)
class ProgramacionAcademicaRow:
    nrc: str
    clave: str
    materia: str
    seccion: str
    dia: str
    hora_inicio: time
    hora_fin: time
    profesor: str
    salon: str


@dataclass(frozen=True)
class ParseProgramacionResult:
    rows: list[ProgramacionAcademicaRow]
    warnings: list[str]


def _squash_cell(value: object) -> str:
    if value is None:
        return ""

    text = str(value).replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def _norm_seccion(raw: str) -> str:
    if not raw:
        return ""

    text = re.sub(r"[Oo]", "0", raw.strip())
    digits = re.sub(r"\D", "", text)

    if not digits:
        return ""

    return digits.zfill(3)[:3]


def _norm_profesor(raw: str) -> str:
    if not raw:
        return ""

    text = raw.replace(" - ", " ")
    text = text.replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def _norm_salon(raw: str) -> str:
    if not raw:
        return ""

    text = raw.strip()
    text = re.sub(r"\s+", "", text)
    return text.upper()


def _split_hora(raw: str) -> tuple[time, time] | None:
    if not raw:
        return None

    text = raw.replace(" ", "")
    match = re.match(r"^(\d{3,4})[-–](\d{3,4})$", text)

    if not match:
        return None

    def to_time(value: str) -> time:
        value = value.zfill(4)
        hour = int(value[:2])
        minute = int(value[2:])
        return time(hour=hour, minute=minute)

    try:
        return to_time(match.group(1)), to_time(match.group(2))
    except ValueError:
        return None


def _expand_dias(raw: str) -> list[str]:
    if not raw:
        return []

    text = raw.strip().upper().replace(" ", "")

    if re.fullmatch(r"[LAMJVS]{1,}", text):
        return list(text)

    dias = [char for char in text if char in "LAMJVS"]
    return dias


def _fila_base_completa(buffer: dict[str, str]) -> bool:
    required = ["NRC", "Clave", "Materia", "Secc", "Días", "Hora", "Profesor", "Salón"]
    return all(buffer.get(key, "").strip() for key in required)


def _find_header_index(rows: list[list[str]]) -> int:
    for index, row in enumerate(rows):
        joined = " ".join(row).upper()

        if (
            "NRC" in joined
            and "CLAVE" in joined
            and "MATERIA" in joined
            and "PROFESOR" in joined
            and "SAL" in joined
        ):
            return index

    return -1


def _map_header_indexes(header: list[str]) -> dict[str, int | None]:
    indexes: dict[str, int | None] = {
        "NRC": None,
        "CLAVE": None,
        "MATERIA": None,
        "SECC": None,
        "DIAS": None,
        "HORA": None,
        "PROFESOR": None,
        "SALON": None,
    }

    for index, name in enumerate(header):
        normalized = name.upper()

        if "NRC" in normalized:
            indexes["NRC"] = index
        elif "CLAVE" in normalized:
            indexes["CLAVE"] = index
        elif "MATERIA" in normalized:
            indexes["MATERIA"] = index
        elif "SECC" in normalized:
            indexes["SECC"] = index
        elif "DÍAS" in normalized or "DIAS" in normalized:
            indexes["DIAS"] = index
        elif "HORA" in normalized:
            indexes["HORA"] = index
        elif "PROFESOR" in normalized:
            indexes["PROFESOR"] = index
        elif "SAL" in normalized:
            indexes["SALON"] = index

    return indexes


def parse_programacion_academica_pdf(path_pdf: str) -> ParseProgramacionResult:
    parsed_rows: list[ProgramacionAcademicaRow] = []
    warnings: list[str] = []

    with pdfplumber.open(path_pdf) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            table_settings_candidates = [
                {
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "snap_tolerance": 3,
                },
                {
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                },
            ]

            tables = None

            for table_settings in table_settings_candidates:
                try:
                    tables = page.extract_tables(table_settings=table_settings)
                except Exception:
                    tables = None

                if tables:
                    break

            if not tables:
                warnings.append(f"Página {page_number}: no se encontraron tablas.")
                continue

            for table in tables:
                rows = [[_squash_cell(cell) for cell in row] for row in table]

                header_index = _find_header_index(rows)

                if header_index == -1:
                    continue

                header = [cell.upper() for cell in rows[header_index]]
                indexes = _map_header_indexes(header)

                if any(value is None for value in indexes.values()):
                    warnings.append(f"Página {page_number}: encabezado no reconocido.")
                    continue

                buffer = {
                    "NRC": "",
                    "Clave": "",
                    "Materia": "",
                    "Secc": "",
                    "Días": "",
                    "Hora": "",
                    "Profesor": "",
                    "Salón": "",
                }

                def flush_if_ready() -> None:
                    if not any(value.strip() for value in buffer.values()):
                        return

                    if not _fila_base_completa(buffer):
                        warnings.append(f"Página {page_number}: fila incompleta ignorada: {buffer}")
                        return

                    seccion = _norm_seccion(buffer["Secc"])
                    profesor = _norm_profesor(buffer["Profesor"])
                    salon = _norm_salon(buffer["Salón"])
                    horas = _split_hora(buffer["Hora"])
                    dias = _expand_dias(buffer["Días"])

                    if not seccion or not profesor or not salon or not horas or not dias:
                        warnings.append(f"Página {page_number}: fila no válida ignorada: {buffer}")
                        return

                    hora_inicio, hora_fin = horas

                    for dia in dias:
                        parsed_rows.append(
                            ProgramacionAcademicaRow(
                                nrc=buffer["NRC"].strip(),
                                clave=buffer["Clave"].strip().upper(),
                                materia=re.sub(r"\s+", " ", buffer["Materia"]).strip(),
                                seccion=seccion,
                                dia=dia,
                                hora_inicio=hora_inicio,
                                hora_fin=hora_fin,
                                profesor=profesor,
                                salon=salon,
                            )
                        )

                    for key in buffer:
                        buffer[key] = ""

                def col(row: list[str], index: int | None) -> str:
                    if index is None or index >= len(row):
                        return ""
                    return row[index]

                for row in rows[header_index + 1:]:
                    joined = " ".join(row).upper()

                    if (
                        "NRC" in joined
                        and "CLAVE" in joined
                        and "MATERIA" in joined
                        and "PROFESOR" in joined
                        and "SAL" in joined
                    ):
                        flush_if_ready()
                        continue

                    current_nrc = col(row, indexes["NRC"])
                    current_clave = col(row, indexes["CLAVE"])
                    current_materia = col(row, indexes["MATERIA"])
                    current_secc = col(row, indexes["SECC"])
                    current_dias = col(row, indexes["DIAS"])
                    current_hora = col(row, indexes["HORA"])
                    current_profesor = col(row, indexes["PROFESOR"])
                    current_salon = col(row, indexes["SALON"])

                    if re.match(r"^\d{5}$", current_nrc.strip()):
                        flush_if_ready()

                        buffer["NRC"] = current_nrc
                        buffer["Clave"] = current_clave
                        buffer["Materia"] = current_materia
                        buffer["Secc"] = current_secc
                        buffer["Días"] = current_dias
                        buffer["Hora"] = current_hora
                        buffer["Profesor"] = current_profesor
                        buffer["Salón"] = current_salon
                    else:
                        if current_clave:
                            buffer["Clave"] = f"{buffer['Clave']} {current_clave}".strip()
                        if current_materia:
                            buffer["Materia"] = f"{buffer['Materia']} {current_materia}".strip()
                        if current_secc:
                            buffer["Secc"] = f"{buffer['Secc']} {current_secc}".strip()
                        if current_dias:
                            buffer["Días"] = f"{buffer['Días']} {current_dias}".strip()
                        if current_hora:
                            buffer["Hora"] = f"{buffer['Hora']} {current_hora}".strip().replace(" ", "")
                        if current_profesor:
                            buffer["Profesor"] = f"{buffer['Profesor']} {current_profesor}".strip()
                        if current_salon:
                            buffer["Salón"] = f"{buffer['Salón']} {current_salon}".strip()

                flush_if_ready()

    return ParseProgramacionResult(rows=parsed_rows, warnings=warnings)