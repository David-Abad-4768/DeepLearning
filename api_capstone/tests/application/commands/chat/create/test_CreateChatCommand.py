import pytest
from mediatr import GenericQuery

from app.application.commands.chat.create.CreateChatCommand import \
    CreateChatCommand
from app.application.models.chat.ChatModel import (CreateChatModel,
                                                   CreateChatResponse)


def test_create_chat_command_is_generic_query_subclass():
    assert issubclass(CreateChatCommand, GenericQuery)


def test_create_chat_command_assigns_chat():
    model = CreateChatModel(title="Test")
    cmd = CreateChatCommand(model)
    assert cmd.chat is model


def test_create_chat_command_missing_argument_raises():
    with pytest.raises(TypeError):
        CreateChatCommand()
