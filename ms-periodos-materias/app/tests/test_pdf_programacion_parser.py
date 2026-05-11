from datetime import time

from app.utils.pdf_programacion_parser import _expand_dias, _norm_seccion, _split_hora


def test_norm_seccion_reemplaza_o_por_cero():
    assert _norm_seccion("OO4") == "004"


def test_norm_seccion_rellena_a_tres_digitos():
    assert _norm_seccion("4") == "004"


def test_split_hora_valida():
    result = _split_hora("1700-1859")

    assert result == (time(17, 0), time(18, 59))


def test_expand_dias_multiples():
    assert _expand_dias("LAV") == ["L", "A", "V"]