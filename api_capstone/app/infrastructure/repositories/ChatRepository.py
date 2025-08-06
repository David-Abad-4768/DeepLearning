from typing import List, Optional

from app.domain.entities.Chat import ChatEntity
from app.infrastructure.database.Database import SessionLocal

from .BaseRepository import BaseRepository


class ChatRepository(BaseRepository[ChatEntity]):
    _instance = None

    def __init__(self, db):
        super().__init__(ChatEntity, db)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls(SessionLocal())
        return cls._instance

    def get_by_chat_id(self, chat_id: str) -> Optional[ChatEntity]:
        return self.db.query(self.model).filter(self.model.chat_id == chat_id).first()

    def get_chats_by_user(self, user_id: str) -> List[ChatEntity]:
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .all()
        )
