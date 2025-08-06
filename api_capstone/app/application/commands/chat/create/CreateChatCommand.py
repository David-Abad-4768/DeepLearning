from mediatr import GenericQuery

from app.application.models.chat.ChatModel import (CreateChatModel,
                                                   CreateChatResponse)


class CreateChatCommand(GenericQuery[CreateChatResponse]):
    def __init__(self, chat: CreateChatModel):
        self.chat = chat
