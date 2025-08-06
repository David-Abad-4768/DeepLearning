from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Chat(BaseModel):
    chat_id: UUID
    title: Optional[str] = None
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateChatModel(BaseModel):
    title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CreateChatResponse(BaseModel):
    chat: Chat
    message: str

    model_config = ConfigDict(from_attributes=True)


class UpdateChatTitleModel(BaseModel):
    chat_id: UUID
    title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UpdateChatTitleResponse(BaseModel):
    chat: Chat
    message: str

    model_config = ConfigDict(from_attributes=True)


class DeleteChatModel(BaseModel):
    chat_id: UUID

    model_config = ConfigDict(from_attributes=True)


class DeleteChatResponse(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)


class ListChatsResponse(BaseModel):
    chats: List[Chat]

    model_config = ConfigDict(from_attributes=True)
