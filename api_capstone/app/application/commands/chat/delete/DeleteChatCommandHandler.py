from mediatr import Mediator

from app.application.models.chat.ChatModel import DeleteChatResponse
from app.core.utils.Logger import get_logger
from app.infrastructure.repositories.ChatRepository import ChatRepository

from .DeleteChatCommand import DeleteChatCommand

logger = get_logger(__name__)


@Mediator.handler
class DeleteChatCommandHandler:
    def __init__(self):
        self.chat_repo = ChatRepository.instance()

    async def handle(self, request: DeleteChatCommand) -> DeleteChatResponse:
        logger.info("Deleting chat %s", request.chat.chat_id)

        self.chat_repo.delete(request.chat.chat_id)

        return DeleteChatResponse(message="Chat deleted successfully.")
