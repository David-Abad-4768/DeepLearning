from typing import List

from mediatr import Mediator

from app.application.models.message.MessageModel import Message
from app.infrastructure.repositories.MessageRepository import MessageRepository

from .GetMessagesPagedQuery import GetMessagesPagedQuery


@Mediator.handler
class GetMessagesPagedQueryHandler:
    """Handles GetMessagesPagedQuery and returns a list of Message DTOs."""

    def __init__(self):
        self.repo = MessageRepository.instance()

    async def handle(self, q: GetMessagesPagedQuery) -> List[Message]:
        rows = self.repo.get_messages_by_chat_paged(
            chat_id=str(q.chat_id),
            limit=q.limit,
            offset=q.offset,
            ascending=q.ascending,
        )
        # Map ORM → Pydantic
        return [Message.model_validate(r, from_attributes=True) for r in rows]
