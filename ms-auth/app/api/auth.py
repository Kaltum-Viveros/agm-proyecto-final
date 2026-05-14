from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_bearer_token
from app.core.responses import error_response, success_response
from app.db.session import get_db
from app.models.enums import UserRole
from app.schemas.auth import (
    AuthUserResponse,
    CreateUserIdentityRequest,
    CreateUserIdentityResponseData,
    ForgotPasswordRequest,
    ForgotPasswordResponseData,
    LoginRequest,
    LoginResponseData,
    LogoutRequest,
    LogoutResponseData,
    RefreshTokenRequest,
    RefreshTokenResponseData,
    ResetPasswordRequest,
    ResetPasswordResponseData,
)
from app.services.auth_service import (
    AccessTokenExpiredError,
    AuthService,
    InactiveUserError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    InvalidPasswordResetTokenError,
    InvalidRefreshTokenError,
    InvalidUserIdentityDataError,
)
from app.services.rbac_service import ForbiddenRoleError

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


@router.get("/me")
def me(
    access_token: str = Depends(get_bearer_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        current_user = auth_service.get_current_user(
            access_token=access_token,
        )

        response_data = AuthUserResponse(**current_user).model_dump(
            mode="json",
        )

        return success_response(
            data=response_data,
            message="Usuario autenticado",
        )

    except AccessTokenExpiredError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Access token expirado",
                error_code="AUTH_ACCESS_TOKEN_EXPIRED",
            ),
        )

    except InvalidAccessTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Access token invalido",
                error_code="AUTH_INVALID_ACCESS_TOKEN",
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


@router.get("/users")
def get_all_users_endpoint(
    access_token: str = Depends(get_bearer_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        # Solo administradores pueden ver todos los usuarios
        auth_service.validate_current_user_roles(
            access_token=access_token,
            allowed_roles=[UserRole.ADMIN],
        )

        users = auth_service.get_all_users()

        return success_response(
            data={"users": users},
            message="Usuarios obtenidos correctamente",
        )

    except AccessTokenExpiredError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Access token expirado",
                error_code="AUTH_ACCESS_TOKEN_EXPIRED",
            ),
        )

    except InvalidAccessTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Access token invalido",
                error_code="AUTH_INVALID_ACCESS_TOKEN",
            ),
        )

    except ForbiddenRoleError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response(
                message="Rol no autorizado",
                error_code="AUTH_ROLE_NOT_ALLOWED",
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


@router.post("/users")
def create_user_identity(
    payload: CreateUserIdentityRequest,
    access_token: str = Depends(get_bearer_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        auth_service.validate_current_user_roles(
            access_token=access_token,
            allowed_roles=[UserRole.ADMIN],
        )

        result = auth_service.create_or_get_user_identity(
            nombre_completo=payload.nombre_completo,
            email=payload.email,
            role=payload.rol,
        )

        response_data = CreateUserIdentityResponseData(**result).model_dump(
            mode="json",
        )

        return success_response(
            data=response_data,
            message="Identidad de usuario procesada correctamente",
        )

    except AccessTokenExpiredError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Access token expirado",
                error_code="AUTH_ACCESS_TOKEN_EXPIRED",
            ),
        )

    except InvalidAccessTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Access token invalido",
                error_code="AUTH_INVALID_ACCESS_TOKEN",
            ),
        )

    except ForbiddenRoleError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response(
                message="Rol no autorizado",
                error_code="AUTH_ROLE_NOT_ALLOWED",
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

    except InvalidUserIdentityDataError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response(
                message="Datos de identidad invalidos",
                error_code="AUTH_INVALID_USER_IDENTITY_DATA",
            ),
        )


@router.post("/logout")
def logout(
    payload: Optional[LogoutRequest] = None,
    access_token: str = Depends(get_bearer_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        refresh_token_value = None

        if payload is not None:
            refresh_token_value = payload.refresh_token

        logout_result = auth_service.logout(
            access_token=access_token,
            refresh_token=refresh_token_value,
        )

        response_data = LogoutResponseData(**logout_result).model_dump(
            mode="json",
        )

        return success_response(
            data=response_data,
            message="Logout exitoso",
        )

    except AccessTokenExpiredError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Access token expirado",
                error_code="AUTH_ACCESS_TOKEN_EXPIRED",
            ),
        )

    except InvalidAccessTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Access token invalido",
                error_code="AUTH_INVALID_ACCESS_TOKEN",
            ),
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


@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    result = auth_service.request_password_reset(
        email=payload.email,
    )

    response_data = ForgotPasswordResponseData(**result).model_dump(
        mode="json",
    )

    return success_response(
        data=response_data,
        message="Solicitud de recuperacion procesada",
    )


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        result = auth_service.reset_password(
            reset_token=payload.reset_token,
            nueva_contrasena=payload.nueva_contrasena,
        )

        response_data = ResetPasswordResponseData(**result).model_dump(
            mode="json",
        )

        return success_response(
            data=response_data,
            message="Contraseña actualizada correctamente",
        )

    except InvalidPasswordResetTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                message="Token de recuperacion invalido",
                error_code="AUTH_INVALID_PASSWORD_RESET_TOKEN",
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