# app/infrastructure/dependencies/Dependencies.py

import logging
from uuid import UUID

from fastapi import HTTPException, Request, status

from app.application.services.AuthService import AuthService
from app.domain.entities.User import UserEntity
from app.infrastructure.database.Database import SessionLocal
from app.infrastructure.repositories.UserRepository import UserRepository

logger = logging.getLogger(__name__)
auth_service = AuthService()


def get_current_user(request: Request) -> UserEntity:
    token = request.cookies.get("access_token")
    if not token:
        logger.debug("No access_token cookie present")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = auth_service.decode_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # valida que sea un UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )

    db = SessionLocal()
    try:
        user = UserRepository(db).get(str(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user
    finally:
        db.close()
