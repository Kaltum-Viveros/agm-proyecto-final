from typing import Any


def success_response(
    data: Any = None,
    message: str = "Operación realizada correctamente",
) -> dict:
    return {
        "success": True,
        "data": data,
        "message": message,
    }


def error_response(
    message: str = "Ocurrió un error",
    data: Any = None,
) -> dict:
    return {
        "success": False,
        "data": data,
        "message": message,
    }