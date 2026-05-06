from decimal import Decimal, ROUND_FLOOR


def redondear_promedio(promedio: Decimal) -> int:
    """
    Regla institucional:
    - fracción >= 0.5 sube
    - fracción < 0.5 baja
    """
    resultado = int((promedio + Decimal("0.5")).to_integral_value(rounding=ROUND_FLOOR))

    if resultado > 10:
        return 10

    if resultado < 0:
        return 0

    return resultado