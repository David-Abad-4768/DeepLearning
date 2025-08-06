import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from app.core.Base import Base


class ChatEntity(Base):
    __tablename__ = "chats"

    chat_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    title = Column(String(100), nullable=True)
    user_id = Column(CHAR(36), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("UserEntity", back_populates="chats")
    messages = relationship(
        "MessageEntity", back_populates="chat", cascade="all, delete-orphan"
    )
