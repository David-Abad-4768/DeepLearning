from datetime import datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.application.models.chat.ChatModel import (Chat, CreateChatModel,
                                                   CreateChatResponse,
                                                   DeleteChatModel,
                                                   DeleteChatResponse,
                                                   ListChatsResponse,
                                                   UpdateChatTitleModel,
                                                   UpdateChatTitleResponse)


def test_chat_model_valid():
    data = {
        "chat_id": uuid4(),
        "title": "Test Chat",
        "user_id": uuid4(),
        "created_at": datetime.utcnow(),
    }
    model = Chat(**data)
    assert isinstance(model.chat_id, UUID)
    assert model.title == "Test Chat"
    assert isinstance(model.user_id, UUID)
    assert isinstance(model.created_at, datetime)


def test_chat_model_missing_required_fields():
    with pytest.raises(ValidationError):
        Chat(title="Only Title")


def test_create_chat_model_defaults_and_assignment():
    m1 = CreateChatModel()
    assert m1.title is None
    m2 = CreateChatModel(title="New Chat")
    assert m2.title == "New Chat"


def test_create_chat_response_valid_and_missing():
    chat = Chat(
        chat_id=uuid4(),
        title="Resp Chat",
        user_id=uuid4(),
        created_at=datetime.utcnow(),
    )
    resp = CreateChatResponse(chat=chat, message="created")
    assert resp.chat is chat
    assert resp.message == "created"
    with pytest.raises(ValidationError):
        CreateChatResponse(chat=chat)


def test_update_chat_title_model_valid_and_missing():
    uid = uuid4()
    m = UpdateChatTitleModel(chat_id=uid, title="Updated")
    assert m.chat_id == uid
    assert m.title == "Updated"
    with pytest.raises(ValidationError):
        UpdateChatTitleModel(title="No ID")


def test_update_chat_title_response_valid_and_missing():
    chat = Chat(
        chat_id=uuid4(),
        title="Before",
        user_id=uuid4(),
        created_at=datetime.utcnow(),
    )
    resp = UpdateChatTitleResponse(chat=chat, message="updated")
    assert resp.chat is chat
    assert resp.message == "updated"
    with pytest.raises(ValidationError):
        UpdateChatTitleResponse(chat=chat)


def test_delete_chat_model_valid_and_missing():
    uid = uuid4()
    m = DeleteChatModel(chat_id=uid)
    assert m.chat_id == uid
    with pytest.raises(ValidationError):
        DeleteChatModel()


def test_delete_chat_response_valid_and_missing():
    r = DeleteChatResponse(message="deleted")
    assert r.message == "deleted"
    with pytest.raises(ValidationError):
        DeleteChatResponse()


def test_list_chats_response_valid_and_invalid():
    chat = Chat(
        chat_id=uuid4(),
        title="C1",
        user_id=uuid4(),
        created_at=datetime.utcnow(),
    )
    r = ListChatsResponse(chats=[chat])
    assert r.chats == [chat]
    with pytest.raises(ValidationError):
        ListChatsResponse(chats=["not a chat"])
