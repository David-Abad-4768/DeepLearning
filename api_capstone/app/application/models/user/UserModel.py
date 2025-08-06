from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    username: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    user_id: UUID | None = None
    username: str
    email: EmailStr
    password: str = Field(exclude=True)

    model_config = ConfigDict(from_attributes=True)


class CreateModel(BaseModel):
    username: str
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class CreateResponse(BaseModel):
    user: User
    message: str

    model_config = ConfigDict(from_attributes=True)


class DeleteModel(BaseModel):
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class DeleteResponse(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)
