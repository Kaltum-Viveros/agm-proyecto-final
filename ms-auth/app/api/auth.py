from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponseData,
    RefreshTokenRequest,
    RefreshTokenResponseData,
)
from app.services.auth_service import (
    AuthService,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def get_auth_service(
    db: Session = Depends(get_db),
) -> AuthService:
    return AuthService(db=db)


@router.post("/login")
def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        login_result = auth_service.login(
            email=payload.email,
            contrasena=payload.contrasena,
        )

        response_data = LoginResponseData(**login_result).model_dump(
            mode="json",
        )

        return success_response(
            data=response_data,
            message="Login exitoso",
        )

    except InvalidCredentialsError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Credenciales invalidas",
                error_code="AUTH_INVALID_CREDENTIALS",
            ),
        )

    except InactiveUserError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response(
                message="Usuario inactivo",
                error_code="AUTH_INACTIVE_USER",
            ),
        )


@router.post("/refresh-token")
def refresh_token(
    payload: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        refresh_result = auth_service.refresh_session(
            refresh_token=payload.refresh_token,
        )

        response_data = RefreshTokenResponseData(**refresh_result).model_dump(
            mode="json",
        )

        return success_response(
            data=response_data,
            message="Sesion renovada correctamente",
        )

    except InvalidRefreshTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Refresh token invalido",
                error_code="AUTH_INVALID_REFRESH_TOKEN",
            ),
        )

    except InactiveUserError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response(
                message="Usuario inactivo",
                error_code="AUTH_INACTIVE_USER",
            ),
        )