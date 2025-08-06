from mediatr import GenericQuery

from app.application.models.message.MessageModel import (CreateMessageModel,
                                                         CreateMessageResponse)


class CreateMessageCommand(GenericQuery[CreateMessageResponse]):
    def __init__(self, payload: CreateMessageModel):
        self.payload = payload
