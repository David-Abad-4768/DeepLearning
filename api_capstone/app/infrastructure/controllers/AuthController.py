import logging

from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from pydantic import BaseModel

from app.application.services.AuthService import AuthService
from app.domain.entities.User import UserEntity
from app.infrastructure.dependencies.Dependencies import get_current_user

logger = logging.getLogger(__name__)
auth_service = AuthService()


class LoginModel(BaseModel):
    username: str
    password: str


class AuthController:
    def __init__(self):
        self.router = APIRouter(tags=["Auth"])

        # POST /auth/login → público
        self.router.post("/login", status_code=status.HTTP_200_OK)(self.login)

        # POST /auth/logout → protegido
        self.router.post("/logout", status_code=status.HTTP_200_OK)(self.logout)

        # GET /auth/verify → protegido
        self.router.get("/verify", status_code=status.HTTP_200_OK)(self.verify_token)

    async def login(self, credentials: LoginModel, response: Response):
        """
        Público: valida credenciales, setea la cookie 'access_token' y sólo devuelve el mensaje.
        """
        logger.info("HTTP POST /auth/login username=%s", credentials.username)
        try:
            auth_service.login_and_set_cookie(
                username=credentials.username,
                password=credentials.password,
                response=response,
            )
            return {"message": "Login successful"}
        except HTTPException:
            raise
        except Exception:
            logger.exception("Login error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def logout(
        self,
        response: Response,
        current_user: UserEntity = Depends(get_current_user),
    ):
        logger.info("HTTP POST /auth/logout user=%s", current_user.user_id)
        auth_service.logout_and_clear_cookie(response)
        return {"message": "Logout successful"}

    async def verify_token(
        self,
        request: Request,
        current_user: UserEntity = Depends(get_current_user),
    ):
        logger.info("HTTP GET /auth/verify user=%s", current_user.user_id)
        payload = auth_service.verify_token_cookie(request)
        return {"valid": True, "payload": payload}
