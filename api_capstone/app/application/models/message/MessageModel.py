from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.types.MessageType import MessageTypeEnum


class Message(BaseModel):
    message_id: UUID
    chat_id: UUID
    content: str
    created_at: datetime
    type: MessageTypeEnum
    image: bool = False

    model_config = ConfigDict(from_attributes=True)


class CreateMessageModel(BaseModel):
    chat_id: UUID
    content: str
    image: bool = False

    model_config = ConfigDict(from_attributes=True)


class CreateMessageResponse(BaseModel):
    client_message: Message
    system_message: Message
    message: str

    model_config = ConfigDict(from_attributes=True)


class MessagePair(BaseModel):
    client: Message
    system: Message

    model_config = ConfigDict(from_attributes=True)


class ListMessagesResponse(BaseModel):
    chat_id: UUID
    messages: List[MessagePair]

    model_config = ConfigDict(from_attributes=True)
