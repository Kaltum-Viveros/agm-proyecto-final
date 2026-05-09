from typing import Optional

from fastapi import Header


def get_bearer_token(
    authorization: Optional[str] = Header(default=None),
) -> str:
    if authorization is None:
        return ""

    parts = authorization.strip().split()

    if len(parts) != 2:
        return ""

    scheme = parts[0]
    token = parts[1]

    if scheme.lower() != "bearer":
        return ""

    return token