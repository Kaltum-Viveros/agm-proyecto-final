from math import ceil
from typing import Any


def get_offset(page: int, limit: int) -> int:
    return (page - 1) * limit


def build_paginated_response(
    items: list[Any],
    total: int,
    page: int,
    limit: int,
) -> dict:
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": ceil(total / limit) if total > 0 else 0,
    }