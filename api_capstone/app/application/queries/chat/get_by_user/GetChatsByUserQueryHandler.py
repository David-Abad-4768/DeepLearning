from typing import List

from mediatr import Mediator

from app.application.models.chat.ChatModel import Chat, ListChatsResponse
from app.application.queries.chat.get_by_user.GetChatsByUserQuery import \
    GetChatsByUserQuery
from app.infrastructure.repositories.ChatRepository import ChatRepository


@Mediator.handler
class GetChatsByUserQueryHandler:
    def __init__(self):
        self.chat_repo = ChatRepository.instance()

    async def handle(self, request: GetChatsByUserQuery) -> ListChatsResponse:
        entities = self.chat_repo.get_chats_by_user(str(request.user_id))
        chats: List[Chat] = [
            Chat.model_validate(e, from_attributes=True) for e in entities
        ]
        return ListChatsResponse(chats=chats)
