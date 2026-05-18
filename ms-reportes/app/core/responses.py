from typing import Any


def success_response(data: Any = None, message: str = "OK") -> dict:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str, error_code: str = "ERROR", data: Any = None) -> dict:
    return {
        "success": False,
        "message": message,
        "error_code": error_code,
        "data": data,
    }
