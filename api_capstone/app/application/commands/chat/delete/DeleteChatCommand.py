from mediatr import GenericQuery

from app.application.models.chat.ChatModel import (DeleteChatModel,
                                                   DeleteChatResponse)


class DeleteChatCommand(GenericQuery[DeleteChatResponse]):
    def __init__(self, chat: DeleteChatModel):
        self.chat = chat
