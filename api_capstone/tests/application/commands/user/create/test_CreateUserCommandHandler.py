# tests/application/commands/create/test_CreateUserCommandHandler.py

from uuid import uuid4

import pytest

from app.application.commands.user.create.CreateUserCommand import \
    CreateCommand
from app.application.commands.user.create.CreateUserCommandHandler import \
    CreateCommandHandler
from app.application.models.user.UserModel import CreateModel, CreateResponse
from app.application.services.AuthService import AuthService
from app.domain.entities.User import UserEntity
from app.infrastructure.repositories.UserRepository import UserRepository


class StubRepoSuccess:
    def __init__(self):
        self.created = None

    def create(self, user: UserEntity):
        self.created = user


class StubRepoFailure:
    def create(self, user: UserEntity):
        raise ValueError("duplicate")


@pytest.fixture(autouse=True)
def stub_hash_password(monkeypatch):
    monkeypatch.setattr(AuthService, "hash_password", lambda pwd: f"hashed-{pwd}")
    yield


@pytest.mark.asyncio
async def test_handle_success(monkeypatch):
    stub_repo = StubRepoSuccess()
    monkeypatch.setattr(UserRepository, "instance", lambda: stub_repo)

    handler = CreateCommandHandler()
    model = CreateModel(username="u", email="e@e.com", password="pw")
    cmd = CreateCommand(model)

    response: CreateResponse = await handler.handle(cmd)

    assert isinstance(stub_repo.created, UserEntity)
    assert stub_repo.created.username == "u"
    assert stub_repo.created.email == "e@e.com"
    assert stub_repo.created.password == "hashed-pw"

    assert isinstance(response, CreateResponse)
    assert response.user.username == "u"
    assert response.user.email == "e@e.com"
    assert response.message == "User created successfully."


@pytest.mark.asyncio
async def test_handle_failure(monkeypatch):
    monkeypatch.setattr(UserRepository, "instance", lambda: StubRepoFailure())

    handler = CreateCommandHandler()
    model = CreateModel(username="x", email="x@e.com", password="p")
    cmd = CreateCommand(model)

    with pytest.raises(ValueError) as exc:
        await handler.handle(cmd)
    assert "Error creating user: duplicate" in str(exc.value)
