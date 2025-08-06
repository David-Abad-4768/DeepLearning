import logging
from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from mediatr import Mediator

from app.application.commands.chat.create.CreateChatCommand import \
    CreateChatCommand
from app.application.commands.chat.delete.DeleteChatCommand import \
    DeleteChatCommand
from app.application.commands.chat.update.UpdateChatCommand import \
    UpdateChatTitleCommand
from app.application.models.chat.ChatModel import (CreateChatModel,
                                                   CreateChatResponse,
                                                   DeleteChatModel,
                                                   DeleteChatResponse,
                                                   ListChatsResponse,
                                                   UpdateChatTitleModel,
                                                   UpdateChatTitleResponse)
from app.application.queries.chat.get_by_user.GetChatsByUserQuery import \
    GetChatsByUserQuery
from app.domain.entities.User import UserEntity
from app.infrastructure.dependencies.Dependencies import get_current_user

logger = logging.getLogger(__name__)


class ChatController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter(tags=["Chats"])

        # GET /chats
        self.router.get(
            "/",
            response_model=ListChatsResponse,
            status_code=status.HTTP_200_OK,
        )(self.list_chats)

        # POST /chats
        self.router.post(
            "/",
            response_model=CreateChatResponse,
            status_code=status.HTTP_201_CREATED,
        )(self.create_chat)

        # PATCH /chats/title
        self.router.patch(
            "/title",
            response_model=UpdateChatTitleResponse,
            status_code=status.HTTP_200_OK,
        )(self.update_title)

        # DELETE /chats
        self.router.delete(
            "/",
            response_model=DeleteChatResponse,
            status_code=status.HTTP_200_OK,
        )(self.delete_chat)

    async def list_chats(
        self,
        current_user: UserEntity = Depends(get_current_user),
    ) -> ListChatsResponse:
        logger.info("HTTP GET /chats by user_id=%s", current_user.user_id)
        try:
            user_uuid = UUID(str(current_user.user_id))
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID",
            )

        return cast(
            ListChatsResponse,
            await self.mediator.send_async(GetChatsByUserQuery(user_uuid)),
        )

    async def create_chat(
        self,
        chat: CreateChatModel,
        current_user: UserEntity = Depends(get_current_user),
    ) -> CreateChatResponse:
        logger.info(
            "HTTP POST /chats user_id=%s title=%s",
            current_user.user_id,
            chat.title,
        )

        chat_with_user = chat.model_copy(update={"user_id": current_user.user_id})

        try:
            return cast(
                CreateChatResponse,
                await self.mediator.send_async(CreateChatCommand(chat_with_user)),
            )
        except ValueError as exc:
            logger.exception("CreateChat error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

    async def update_title(
        self,
        update: UpdateChatTitleModel,
        current_user: UserEntity = Depends(get_current_user),
    ) -> UpdateChatTitleResponse:
        logger.info(
            "HTTP PATCH /chats/title chat_id=%s title=%s by user_id=%s",
            update.chat_id,
            update.title,
            current_user.user_id,
        )
        try:
            return cast(
                UpdateChatTitleResponse,
                await self.mediator.send_async(UpdateChatTitleCommand(update)),
            )
        except ValueError as exc:
            logger.exception("UpdateChatTitle error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

    async def delete_chat(
        self,
        delete: DeleteChatModel,
        current_user: UserEntity = Depends(get_current_user),
    ) -> DeleteChatResponse:
        logger.info(
            "HTTP DELETE /chats chat_id=%s by user_id=%s",
            delete.chat_id,
            current_user.user_id,
        )
        try:
            return cast(
                DeleteChatResponse,
                await self.mediator.send_async(DeleteChatCommand(delete)),
            )
        except ValueError as exc:
            logger.exception("DeleteChat error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )
