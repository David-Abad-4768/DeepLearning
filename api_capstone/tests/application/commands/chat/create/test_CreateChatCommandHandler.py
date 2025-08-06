from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.application.commands.chat.create.CreateChatCommand import \
    CreateChatCommand
from app.application.commands.chat.create.CreateChatCommandHandler import \
    CreateChatCommandHandler
from app.application.models.chat.ChatModel import CreateChatResponse
from app.infrastructure.repositories.ChatRepository import ChatRepository


class StubRepo:
    def __init__(self, fail=False):
        self.created = None
        self.fail = fail

    def create(self, chat_entity):
        if self.fail:
            raise RuntimeError("DB error")
        self.created = chat_entity


class StubEntity:
    def __init__(self, title, user_id):
        self.chat_id = uuid4()
        self.title = title
        self.user_id = user_id
        self.created_at = datetime.utcnow()


@pytest.fixture
def stub_repo_success(monkeypatch):
    repo = StubRepo()
    monkeypatch.setattr(ChatRepository, "instance", lambda: repo)
    return repo


@pytest.fixture
def stub_repo_failure(monkeypatch):
    repo = StubRepo(fail=True)
    monkeypatch.setattr(ChatRepository, "instance", lambda: repo)
    return repo


@pytest.fixture(autouse=True)
def stub_chat_entity(monkeypatch):
    import app.application.commands.chat.create.CreateChatCommandHandler as module

    monkeypatch.setattr(module, "ChatEntity", StubEntity)
    yield


@pytest.mark.asyncio
async def test_handle_success_populates_chat_id(stub_repo_success):
    handler = CreateChatCommandHandler()
    uid = uuid4()
    chat_model = SimpleNamespace(title="Room X", user_id=uid)
    cmd = CreateChatCommand(chat_model)

    response: CreateChatResponse = await handler.handle(cmd)

    # Ensure repository received the StubEntity with matching user_id
    assert isinstance(stub_repo_success.created, StubEntity)
    assert stub_repo_success.created.title == "Room X"
    assert stub_repo_success.created.user_id == str(uid)

    # Ensure response.chat.chat_id matches the created entity's id
    assert response.chat.chat_id == stub_repo_success.created.chat_id
    assert response.chat.user_id == uid
    assert response.chat.title == "Room X"
    assert response.message == "Chat created successfully."


@pytest.mark.asyncio
async def test_handle_failure_raises(monkeypatch, stub_repo_failure):
    handler = CreateChatCommandHandler()
    cmd = CreateChatCommand(SimpleNamespace(title="Err", user_id=uuid4()))

    with pytest.raises(RuntimeError) as exc:
        await handler.handle(cmd)
    assert "DB error" in str(exc.value)
