from mediatr import GenericQuery

from app.application.models.chat.ChatModel import (UpdateChatTitleModel,
                                                   UpdateChatTitleResponse)


class UpdateChatTitleCommand(GenericQuery[UpdateChatTitleResponse]):
    def __init__(self, chat: UpdateChatTitleModel):
        self.chat = chat
