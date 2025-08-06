import pytest
from mediatr import GenericQuery

from app.application.commands.user.create.CreateUserCommand import \
    CreateCommand
from app.application.models.user.UserModel import CreateModel, CreateResponse


def test_create_command_is_generic_query_subclass():
    assert issubclass(CreateCommand, GenericQuery)


def test_create_command_assigns_user():
    user = CreateModel(username="u", email="u@example.com", password="p")
    cmd = CreateCommand(user)
    assert cmd.user is user


def test_create_command_missing_user_raises_type_error():
    with pytest.raises(TypeError):
        CreateCommand()
