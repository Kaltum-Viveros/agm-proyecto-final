from contextlib import contextmanager
from typing import Callable, Iterator, Optional
from uuid import UUID

from app.db.session import SessionLocal
from app.grpc.generated import auth_pb2, auth_pb2_grpc
from app.services.auth_service import (
    AccessTokenExpiredError,
    AuthService,
    InactiveUserError,
    InvalidAccessTokenError,
    InvalidUserIdentityDataError,
)


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
    def __init__(
        self,
        auth_service_factory: Optional[Callable[[], AuthService]] = None,
    ) -> None:
        self.auth_service_factory = auth_service_factory

    @contextmanager
    def _get_auth_service(self) -> Iterator[AuthService]:
        if self.auth_service_factory is not None:
            yield self.auth_service_factory()
            return

        db = SessionLocal()

        try:
            yield AuthService(db=db)
        finally:
            db.close()

    def ValidateToken(
        self,
        request,
        context,
    ):
        with self._get_auth_service() as auth_service:
            try:
                claims = auth_service.validate_access_token_claims(
                    access_token=request.token,
                )

                return auth_pb2.ValidateTokenResponse(
                    valid=True,
                    claims=auth_pb2.UserClaims(
                        user_id=claims["user_id"],
                        email=claims["email"],
                        role=claims["role"],
                        jti=claims["jti"],
                        activo=claims["activo"],
                    ),
                    error_code="",
                    message="Token valido",
                )

            except AccessTokenExpiredError:
                return auth_pb2.ValidateTokenResponse(
                    valid=False,
                    claims=auth_pb2.UserClaims(),
                    error_code="AUTH_ACCESS_TOKEN_EXPIRED",
                    message="Access token expirado",
                )

            except InvalidAccessTokenError:
                return auth_pb2.ValidateTokenResponse(
                    valid=False,
                    claims=auth_pb2.UserClaims(),
                    error_code="AUTH_INVALID_ACCESS_TOKEN",
                    message="Access token invalido",
                )

            except InactiveUserError:
                return auth_pb2.ValidateTokenResponse(
                    valid=False,
                    claims=auth_pb2.UserClaims(),
                    error_code="AUTH_INACTIVE_USER",
                    message="Usuario inactivo",
                )

    def GetUserById(
        self,
        request,
        context,
    ):
        try:
            user_id = UUID(str(request.user_id))
        except ValueError:
            return auth_pb2.GetUserByIdResponse(
                found=False,
                user=auth_pb2.UserProfile(),
                error_code="AUTH_INVALID_USER_ID",
                message="User ID invalido",
            )

        with self._get_auth_service() as auth_service:
            user = auth_service.get_user_profile_by_id(user_id)

            if user is None:
                return auth_pb2.GetUserByIdResponse(
                    found=False,
                    user=auth_pb2.UserProfile(),
                    error_code="AUTH_USER_NOT_FOUND",
                    message="Usuario no encontrado",
                )

            return auth_pb2.GetUserByIdResponse(
                found=True,
                user=self._build_user_profile(user),
                error_code="",
                message="Usuario encontrado",
            )

    def CheckRole(
        self,
        request,
        context,
    ):
        try:
            user_id = UUID(str(request.user_id))
        except ValueError:
            return auth_pb2.CheckRoleResponse(
                allowed=False,
                error_code="AUTH_INVALID_USER_ID",
                message="User ID invalido",
            )

        with self._get_auth_service() as auth_service:
            allowed = auth_service.check_user_role(
                user_id=user_id,
                role=request.role,
            )

            if not allowed:
                return auth_pb2.CheckRoleResponse(
                    allowed=False,
                    error_code="AUTH_ROLE_NOT_ALLOWED",
                    message="Rol no autorizado",
                )

            return auth_pb2.CheckRoleResponse(
                allowed=True,
                error_code="",
                message="Rol autorizado",
            )

    def CreateOrGetUserIdentity(
        self,
        request,
        context,
    ):
        with self._get_auth_service() as auth_service:
            try:
                result = auth_service.create_or_get_user_identity(
                    nombre_completo=request.nombre_completo,
                    email=request.email,
                    role=request.role,
                )

                return auth_pb2.CreateOrGetUserIdentityResponse(
                    created=result["created"],
                    user=self._build_user_profile(result["user"]),
                    temporary_password=result["temporary_password"],
                    error_code="",
                    message="Identidad procesada correctamente",
                )

            except InvalidUserIdentityDataError as exc:
                return auth_pb2.CreateOrGetUserIdentityResponse(
                    created=False,
                    user=auth_pb2.UserProfile(),
                    temporary_password="",
                    error_code="AUTH_INVALID_USER_IDENTITY_DATA",
                    message=str(exc),
                )

    def _build_user_profile(
        self,
        user,
    ):
        return auth_pb2.UserProfile(
            user_id=user["user_id"],
            nombre_completo=user["nombre_completo"],
            email=user["email"],
            role=user["rol"],
            activo=user["activo"],
        )