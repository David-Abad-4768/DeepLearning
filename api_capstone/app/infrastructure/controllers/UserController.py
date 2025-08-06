import logging
from typing import cast

from fastapi import APIRouter, HTTPException, status
from mediatr import Mediator

from app.application.commands.user.create.CreateUserCommand import \
    CreateCommand
from app.application.models.user.UserModel import CreateModel, CreateResponse

logger = logging.getLogger(__name__)


class UserController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter(tags=["Users"])

        # POST /users
        self.router.post(
            "/",
            response_model=CreateResponse,
            status_code=status.HTTP_201_CREATED,
        )(self.create_user)

    async def create_user(self, user: CreateModel) -> CreateResponse:
        logger.info("HTTP POST /users username=%s", user.username)
        try:
            return cast(
                CreateResponse, await self.mediator.send_async(CreateCommand(user))
            )
        except ValueError as exc:
            logger.exception("CreateUser error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )
