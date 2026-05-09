from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(
        ...,
        min_length=3,
        max_length=150,
    )
    contrasena: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        ...,
        min_length=1,
    )


class AuthUserResponse(BaseModel):
    user_id: str
    nombre_completo: str
    email: str
    rol: str
    activo: bool


class LoginResponseData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_expires_at: datetime
    user: AuthUserResponse


class RefreshTokenResponseData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_expires_at: datetime
    user: AuthUserResponse