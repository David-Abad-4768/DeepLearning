from typing import Optional

from app.domain.entities.User import UserEntity
from app.infrastructure.database.Database import SessionLocal

from .BaseRepository import BaseRepository


class UserRepository(BaseRepository[UserEntity]):
    _instance = None

    def __init__(self, db):
        super().__init__(UserEntity, db)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls(SessionLocal())
        return cls._instance

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        return self.db.query(self.model).filter(self.model.username == username).first()
