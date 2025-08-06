from typing import Optional
from uuid import UUID

from mediatr import Mediator

from app.application.models.chat.ChatModel import Chat, UpdateChatTitleResponse
from app.core.utils.Logger import get_logger
from app.domain.entities.Chat import ChatEntity
from app.infrastructure.repositories.ChatRepository import ChatRepository

from .UpdateChatCommand import UpdateChatTitleCommand

logger = get_logger(__name__)


@Mediator.handler
class UpdateChatTitleCommandHandler:
    def __init__(self):
        self.chat_repo = ChatRepository.instance()

    async def handle(self, request: UpdateChatTitleCommand) -> UpdateChatTitleResponse:
        chat_id: UUID = request.chat.chat_id
        logger.info("Updating chat %s title", chat_id)

        chat_entity: ChatEntity = self.chat_repo.get(str(chat_id))

        setattr(chat_entity, "title", request.chat.title)

        self.chat_repo.update(chat_entity)

        return UpdateChatTitleResponse(
            chat=Chat.model_validate(chat_entity, from_attributes=True),
            message="Chat title updated.",
        )
