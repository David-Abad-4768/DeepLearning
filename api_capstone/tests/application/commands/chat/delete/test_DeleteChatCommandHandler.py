from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.application.commands.chat.delete.DeleteChatCommand import \
    DeleteChatCommand
from app.application.commands.chat.delete.DeleteChatCommandHandler import \
    DeleteChatCommandHandler
from app.application.models.chat.ChatModel import DeleteChatResponse
from app.infrastructure.repositories.ChatRepository import ChatRepository


class StubRepo:
    def __init__(self, fail=False):
        self.deleted_id = None
        self.fail = fail

    def delete(self, chat_id):
        if self.fail:
            raise RuntimeError("delete error")
        self.deleted_id = chat_id


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


@pytest.mark.asyncio
async def test_handle_success(stub_repo_success):
    handler = DeleteChatCommandHandler()
    chat_id = uuid4()
    cmd = DeleteChatCommand(SimpleNamespace(chat_id=chat_id))

    response: DeleteChatResponse = await handler.handle(cmd)

    assert stub_repo_success.deleted_id == chat_id
    assert isinstance(response, DeleteChatResponse)
    assert response.message == "Chat deleted successfully."


@pytest.mark.asyncio
async def test_handle_failure(stub_repo_failure):
    handler = DeleteChatCommandHandler()
    chat_id = uuid4()
    cmd = DeleteChatCommand(SimpleNamespace(chat_id=chat_id))

    with pytest.raises(RuntimeError) as exc:
        await handler.handle(cmd)
    assert "delete error" in str(exc.value)
