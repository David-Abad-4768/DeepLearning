import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from app.core.Base import Base


class UserEntity(Base):
    __tablename__ = "users"

    user_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    chats = relationship(
        "ChatEntity", back_populates="user", cascade="all, delete-orphan"
    )
