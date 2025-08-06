import logging
from typing import List, Tuple

from app.domain.entities.Message import MessageEntity, MessageTypeEnum
from app.infrastructure.database.Database import SessionLocal

from .BaseRepository import BaseRepository

logger = logging.getLogger(__name__)


class MessageRepository(BaseRepository[MessageEntity]):
    _instance = None

    def __init__(self, db):
        super().__init__(MessageEntity, db)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls(SessionLocal())
        return cls._instance

    def create_many(self, objs: list[MessageEntity]) -> list[MessageEntity]:
        return super().create_many(objs)

    def get_messages_by_chat_paged(
        self,
        chat_id: str,
        limit: int,
        offset: int,
        ascending: bool = False,
    ) -> List[MessageEntity]:
        order_clause = (
            self.model.created_at.asc() if ascending else self.model.created_at.desc()
        )

        logger.info(
            "Fetching messages chat_id=%s limit=%d offset=%d", chat_id, limit, offset
        )
        return (
            self.db.query(self.model)
            .filter(self.model.chat_id == chat_id)
            .order_by(order_clause, self.model.message_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
