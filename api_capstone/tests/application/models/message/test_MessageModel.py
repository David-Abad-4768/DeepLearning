from datetime import datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.application.models.message.MessageModel import (CreateMessageModel,
                                                         CreateMessageResponse,
                                                         ListMessagesResponse,
                                                         Message, MessagePair)
from app.domain.types.MessageType import MessageTypeEnum


def make_message():
    return Message(
        message_id=uuid4(),
        chat_id=uuid4(),
        content="text",
        created_at=datetime.utcnow(),
        type=MessageTypeEnum.CLIENT,
        image=True,
    )


def test_message_model_valid_and_missing():
    msg = make_message()
    assert isinstance(msg.message_id, UUID)
    assert isinstance(msg.chat_id, UUID)
    assert msg.content == "text"
    assert isinstance(msg.created_at, datetime)
    assert msg.type is MessageTypeEnum.CLIENT
    assert msg.image is True
    with pytest.raises(ValidationError):
        Message(content="no ids")


def test_create_message_model_valid_and_missing_fields():
    uid = uuid4()
    m = CreateMessageModel(chat_id=uid, content="hi")
    assert m.chat_id == uid
    assert m.content == "hi"
    assert m.image is False
    with pytest.raises(ValidationError):
        CreateMessageModel(content="hi")
    with pytest.raises(ValidationError):
        CreateMessageModel(chat_id=uid)


def test_create_message_response_valid_and_missing():
    client = make_message()
    system = make_message()
    resp = CreateMessageResponse(
        client_message=client, system_message=system, message="ok"
    )
    assert resp.client_message is client
    assert resp.system_message is system
    assert resp.message == "ok"
    with pytest.raises(ValidationError):
        CreateMessageResponse(client_message=client, message="ok")


def test_message_pair_valid_and_missing():
    client = make_message()
    system = make_message()
    pair = MessagePair(client=client, system=system)
    assert pair.client is client
    assert pair.system is system
    with pytest.raises(ValidationError):
        MessagePair(client=client)


def test_list_messages_response_valid_and_invalid():
    uid = uuid4()
    pair = MessagePair(client=make_message(), system=make_message())
    resp = ListMessagesResponse(chat_id=uid, messages=[pair])
    assert resp.chat_id == uid
    assert resp.messages == [pair]
    with pytest.raises(ValidationError):
        ListMessagesResponse(chat_id=uid, messages=["not a pair"])
