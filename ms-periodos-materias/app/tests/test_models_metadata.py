import app.models  # noqa: F401
from app.db.base import Base

# prueba para verificar que las tablas y columnas esperadas estén registradas en el metadata de SQLAlchemy
def test_expected_tables_are_registered_in_metadata():
    expected_tables = {
        "periodos",
        "planes_estudio",
        "materias_catalogo",
        "materia_plan_estudio",
        "materias_ofertadas",
        "materia_horarios",
    }

    assert expected_tables.issubset(set(Base.metadata.tables.keys()))

# prueba para verificar que las columnas esperadas estén registradas en el metadata de SQLAlchemy para cada tabla
def test_periodos_table_has_expected_columns():
    table = Base.metadata.tables["periodos"]

    expected_columns = {
        "periodo_id",
        "nombre",
        "fecha_inicio",
        "fecha_fin",
        "activo",
    }

    assert expected_columns.issubset(set(table.columns.keys()))

# prueba para verificar que las columnas esperadas estén registradas en el metadata de SQLAlchemy para cada tabla
def test_materias_ofertadas_table_has_expected_columns():
    table = Base.metadata.tables["materias_ofertadas"]

    expected_columns = {
        "materia_ofertada_id",
        "periodo_id",
        "materia_catalogo_id",
        "nrc",
        "seccion",
        "docente_id",
        "docente_nombre",
        "estado",
    }

    assert expected_columns.issubset(set(table.columns.keys()))

# prueba para verificar que las columnas esperadas estén registradas en el metadata de SQLAlchemy para cada tabla
def test_materia_horarios_table_has_expected_columns():
    table = Base.metadata.tables["materia_horarios"]

    expected_columns = {
        "materia_horario_id",
        "materia_ofertada_id",
        "dia",
        "hora_inicio",
        "hora_fin",
        "salon",
    }

    assert expected_columns.issubset(set(table.columns.keys()))