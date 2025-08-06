from mediatr import Mediator

from app.application.models.chat.ChatModel import Chat, CreateChatResponse
from app.core.utils.Logger import get_logger
from app.domain.entities.Chat import ChatEntity
from app.infrastructure.repositories.ChatRepository import ChatRepository

from .CreateChatCommand import CreateChatCommand

logger = get_logger(__name__)


@Mediator.handler
class CreateChatCommandHandler:
    def __init__(self):
        self.chat_repo = ChatRepository.instance()

    async def handle(self, request: CreateChatCommand) -> CreateChatResponse:
        logger.info("Creating chat for user %s", request.chat.user_id)

        entity = ChatEntity(
            title=request.chat.title,
            user_id=str(request.chat.user_id),
        )

        self.chat_repo.create(entity)

        return CreateChatResponse(
            chat=Chat.model_validate(entity, from_attributes=True),
            message="Chat created successfully.",
        )
