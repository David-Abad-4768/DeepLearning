from uuid import UUID

from mediatr import GenericQuery

from app.application.models.chat.ChatModel import ListChatsResponse


class GetChatsByUserQuery(GenericQuery[ListChatsResponse]):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
