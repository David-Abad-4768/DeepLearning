import logging
from typing import List, cast
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from mediatr import Mediator

from app.application.commands.message.create.CreateMessageCommand import \
    CreateMessageCommand
from app.application.models.message.MessageModel import (CreateMessageModel,
                                                         CreateMessageResponse,
                                                         Message)
from app.application.queries.message.get_messages_paged_query.GetMessagesPagedQuery import \
    GetMessagesPagedQuery

logger = logging.getLogger(__name__)


class MessageController:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter(tags=["Messages"])

        self.router.post(
            "/",
            response_model=CreateMessageResponse,
            status_code=status.HTTP_201_CREATED,
        )(self.create_message)

        self.router.get(
            "/chats/{chat_id}/messages",
            response_model=List[Message],
            status_code=status.HTTP_200_OK,
        )(self.list_messages)

    async def create_message(self, msg: CreateMessageModel) -> CreateMessageResponse:
        logger.info("HTTP POST /messages chat_id=%s", msg.chat_id)
        try:
            return cast(
                CreateMessageResponse,
                await self.mediator.send_async(CreateMessageCommand(msg)),
            )
        except ValueError as exc:
            logger.exception("CreateMessage error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

    async def list_messages(
        self,
        chat_id: UUID,
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ) -> List[Message]:
        logger.info(
            "HTTP GET /chats/%s/messages limit=%d offset=%d", chat_id, limit, offset
        )
        try:
            return cast(
                List[Message],
                await self.mediator.send_async(
                    GetMessagesPagedQuery(
                        chat_id=chat_id,
                        limit=limit,
                        offset=offset,
                        ascending=False,  # DESC by default
                    )
                ),
            )
        except ValueError as exc:
            logger.exception("ListMessages error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )
