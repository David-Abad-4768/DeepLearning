import importlib
import uuid
from datetime import datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.dialects.mysql import CHAR

from app.core.Base import Base
from app.domain.entities.Chat import ChatEntity

importlib.import_module("app.domain.entities.User")
importlib.import_module("app.domain.entities.Message")


def test_chat_entity_mapping_and_defaults():
    mapper = inspect(ChatEntity)
    table = mapper.local_table
    assert table.name == "chats"

    id_col = table.c.chat_id
    assert id_col.primary_key
    assert not id_col.nullable
    assert id_col.unique
    assert isinstance(id_col.type, CHAR)
    assert id_col.type.length == 36
    default_id = id_col.default.arg
    assert callable(default_id)
    gen_id = default_id(None)
    assert isinstance(gen_id, str)
    assert uuid.UUID(gen_id)

    title_col = table.c.title
    assert title_col.nullable
    assert title_col.type.length == 100

    user_id_col = table.c.user_id
    assert not user_id_col.nullable
    assert isinstance(user_id_col.type, CHAR)
    assert user_id_col.type.length == 36
    fks = list(user_id_col.foreign_keys)
    assert any(
        fk.column.table.name == "users" and fk.column.name == "user_id" for fk in fks
    )

    created_at_col = table.c.created_at
    assert not created_at_col.nullable
    default_dt = created_at_col.default.arg
    assert callable(default_dt)
    dt = default_dt(None)
    assert isinstance(dt, datetime)


def test_chat_entity_relationships():
    mapper = inspect(ChatEntity)
    rel_user = mapper.relationships["user"]
    assert rel_user.argument == "UserEntity"
    assert rel_user.back_populates == "chats"

    rel_msgs = mapper.relationships["messages"]
    assert rel_msgs.argument == "MessageEntity"
    assert rel_msgs.back_populates == "chat"
    assert "delete-orphan" in str(rel_msgs.cascade)
