from typing import List
from uuid import UUID

from mediatr import GenericQuery

from app.application.models.message.MessageModel import Message


class GetMessagesPagedQuery(GenericQuery[List[Message]]):
    def __init__(
        self, chat_id: UUID, limit: int = 20, offset: int = 0, ascending: bool = False
    ):
        self.chat_id = chat_id
        self.limit = limit
        self.offset = offset
        self.ascending = ascending
