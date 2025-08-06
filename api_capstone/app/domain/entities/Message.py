import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from app.core.Base import Base
from app.domain.types.MessageType import MessageTypeEnum


class MessageEntity(Base):
    __tablename__ = "messages"

    message_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    chat_id = Column(CHAR(36), ForeignKey("chats.chat_id"), nullable=False)
    content = Column(Text, nullable=False)
    image = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    type = Column(Enum(MessageTypeEnum, name="message_type_enum"), nullable=False)

    chat = relationship("ChatEntity", back_populates="messages")
