import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Tuple

from fastapi import HTTPException, Request, Response, status
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.domain.entities.User import UserEntity
from app.infrastructure.database.Database import SessionLocal
from app.infrastructure.repositories.UserRepository import UserRepository
from app.infrastructure.Settings import settings

logger = logging.getLogger(__name__)
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self) -> None:
        self.db = SessionLocal()
        self.user_repository = UserRepository(self.db)

    def authenticate_user(self, username: str, password: str) -> Optional[UserEntity]:
        try:
            user = self.user_repository.get_by_username(username)
            if not user or not self._verify_password(password, user.password):
                return None
            return user
        finally:
            self.db.close()

    def create_access_token(
        self, data: dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=24))
        to_encode["exp"] = expire
        token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        logger.debug(
            "JWT issued for subject=%s, expires_at=%s",
            data.get("sub"),
            expire.isoformat(),
        )
        return token

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
        except ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            ) from exc
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from exc

    def _verify_password(self, plain: str, hashed: Any) -> bool:
        return _pwd_ctx.verify(plain, hashed)  # type: ignore[arg-type]

    @staticmethod
    def hash_password(password: str) -> str:
        return _pwd_ctx.hash(password)

    def login_and_set_cookie(
        self,
        username: str,
        password: str,
        response: Response,
        *,
        token_name: str = "access_token",
        expires_delta: Optional[timedelta] = None,
    ) -> Tuple[UserEntity, str]:
        user = self.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        expires_delta = expires_delta or timedelta(hours=24)
        payload = {"sub": str(user.user_id)}
        token = self.create_access_token(payload, expires_delta=expires_delta)

        response.set_cookie(
            key=token_name,
            value=token,
            max_age=int(expires_delta.total_seconds()),
            httponly=True,
            secure=True,
            samesite="none",
        )
        return user, token

    def logout_and_clear_cookie(
        self, response: Response, *, token_name: str = "access_token"
    ) -> None:
        response.delete_cookie(key=token_name)

    def verify_token_cookie(
        self, request: Request, *, token_name: str = "access_token"
    ) -> dict[str, Any]:
        token = request.cookies.get(token_name)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not found in cookies",
            )
        return self.decode_token(token)
