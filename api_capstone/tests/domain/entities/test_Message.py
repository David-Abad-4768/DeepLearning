import importlib
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Enum, Text, inspect
from sqlalchemy.dialects.mysql import CHAR

from app.core.Base import Base
from app.domain.entities.Message import MessageEntity
from app.domain.types.MessageType import MessageTypeEnum

importlib.import_module("app.domain.entities.Chat")


def test_message_entity_mapping_and_defaults():
    mapper = inspect(MessageEntity)
    table = mapper.local_table
    assert table.name == "messages"

    id_col = table.c.message_id
    assert id_col.primary_key
    assert not id_col.nullable
    assert id_col.unique
    assert isinstance(id_col.type, CHAR)
    assert id_col.type.length == 36
    default_id = id_col.default.arg
    assert callable(default_id)
    mid = default_id(None)
    assert isinstance(mid, str)
    assert uuid.UUID(mid)

    chat_id_col = table.c.chat_id
    assert not chat_id_col.nullable
    assert isinstance(chat_id_col.type, CHAR)
    assert chat_id_col.type.length == 36
    fks = list(chat_id_col.foreign_keys)
    assert any(
        fk.column.table.name == "chats" and fk.column.name == "chat_id" for fk in fks
    )

    content_col = table.c.content
    assert not content_col.nullable
    assert isinstance(content_col.type, Text)

    image_col = table.c.image
    assert not image_col.nullable
    assert isinstance(image_col.type, Boolean)
    assert image_col.default.arg is False

    created_at_col = table.c.created_at
    assert not created_at_col.nullable
    dt_default = created_at_col.default.arg
    assert callable(dt_default)
    dt = dt_default(None)
    assert isinstance(dt, datetime)

    type_col = table.c.type
    assert not type_col.nullable
    assert isinstance(type_col.type, Enum)
    assert type_col.type.name == "message_type_enum"


def test_message_entity_relationship():
    mapper = inspect(MessageEntity)
    rel = mapper.relationships["chat"]
    assert rel.argument == "ChatEntity"
    assert rel.back_populates == "messages"
