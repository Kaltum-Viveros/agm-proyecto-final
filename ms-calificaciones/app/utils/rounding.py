from decimal import Decimal, ROUND_FLOOR


def redondear_promedio(promedio: Decimal) -> int:
    """
    Regla institucional ajustada:
    - Si el promedio es menor a 6, no puede subir a 6.
      Ej: 5.9 -> 5
    - Si el promedio es 6 o mayor, se aplica redondeo normal:
      fracción >= 0.5 sube, fracción < 0.5 baja.
      Ej: 6.4 -> 6, 6.5 -> 7, 8.7 -> 9
    """

    if promedio < Decimal("6"):
        return int(promedio.to_integral_value(rounding=ROUND_FLOOR))

    resultado = int((promedio + Decimal("0.5")).to_integral_value(rounding=ROUND_FLOOR))

    if resultado > 10:
        return 10

    return resultado