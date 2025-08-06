from uuid import uuid4

import pytest
from mediatr import GenericQuery

from app.application.commands.chat.delete.DeleteChatCommand import \
    DeleteChatCommand
from app.application.models.chat.ChatModel import (DeleteChatModel,
                                                   DeleteChatResponse)


def test_delete_chat_command_is_generic_query_subclass():
    assert issubclass(DeleteChatCommand, GenericQuery)


def test_delete_chat_command_assigns_model():
    model = DeleteChatModel(chat_id=uuid4())
    cmd = DeleteChatCommand(model)
    assert cmd.chat is model


def test_delete_chat_command_missing_argument_raises_type_error():
    with pytest.raises(TypeError):
        DeleteChatCommand()
