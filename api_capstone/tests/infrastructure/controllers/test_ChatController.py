from datetime import datetime
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from starlette.testclient import TestClient

from app.application.commands.chat.create.CreateChatCommand import \
    CreateChatCommand
from app.application.commands.chat.delete.DeleteChatCommand import \
    DeleteChatCommand
from app.application.commands.chat.update.UpdateChatCommand import \
    UpdateChatTitleCommand
from app.application.queries.chat.get_by_user.GetChatsByUserQuery import \
    GetChatsByUserQuery
from app.infrastructure.controllers.ChatController import ChatController
from app.infrastructure.dependencies.Dependencies import get_current_user


class DummyMediator:
    def __init__(self, result=None, exc=None):
        self.result = result
        self.exc = exc
        self.sent = []

    async def send_async(self, command):
        self.sent.append(command)
        if self.exc:
            raise self.exc
        return self.result


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture(autouse=True)
def override_user_dependency(app):
    user_id = str(uuid4())
    app.dependency_overrides[get_current_user] = lambda: type(
        "U", (), {"user_id": user_id}
    )()
    return


def test_list_chats_success(app, client):
    user = app.dependency_overrides[get_current_user]()
    chat_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    expected = {
        "chats": [
            {
                "chat_id": chat_id,
                "title": "hello",
                "user_id": user.user_id,
                "created_at": now,
            }
        ],
        "total": 1,
    }
    mediator = DummyMediator(result=expected)
    controller = ChatController(mediator)
    app.include_router(controller.router, prefix="/chats")

    response = client.get("/chats/")
    assert response.status_code == status.HTTP_200_OK
    resp_json = response.json()
    assert resp_json["chats"] == expected["chats"]
    assert isinstance(mediator.sent[0], GetChatsByUserQuery)


@pytest.mark.parametrize("invalid_id", ["", "not-uuid"])
def test_list_chats_invalid_user_id(app, client, invalid_id):
    app.dependency_overrides[get_current_user] = lambda: type(
        "U", (), {"user_id": invalid_id}
    )()
    mediator = DummyMediator(result={})
    controller = ChatController(mediator)
    app.include_router(controller.router, prefix="/chats")

    response = client.get("/chats/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid user ID"


def test_create_chat_success(app, client):
    user = app.dependency_overrides[get_current_user]()
    chat_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    result = {
        "chat": {
            "chat_id": chat_id,
            "title": "new",
            "user_id": user.user_id,
            "created_at": now,
        },
        "message": "Created",
    }
    mediator = DummyMediator(result=result)
    controller = ChatController(mediator)
    app.include_router(controller.router, prefix="/chats")

    response = client.post("/chats/", json={"title": "new"})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == result
    assert isinstance(mediator.sent[0], CreateChatCommand)


@pytest.mark.parametrize(
    "cmd_class,verb,path,payload",
    [
        (
            UpdateChatTitleCommand,
            "patch",
            "/title",
            {"chat_id": str(uuid4()), "title": "upd"},
        ),
    ],
)
def test_commands_success(app, client, cmd_class, verb, path, payload):
    if cmd_class is UpdateChatTitleCommand:
        chat_id = payload["chat_id"]
        now = datetime.utcnow().isoformat()
        result = {
            "chat": {
                "chat_id": chat_id,
                "title": payload["title"],
                "user_id": app.dependency_overrides[get_current_user]().user_id,
                "created_at": now,
            },
            "message": "Updated",
        }
        expected_status = status.HTTP_200_OK
    else:
        result = {"success": True, "message": "Deleted"}
        expected_status = status.HTTP_200_OK

    mediator = DummyMediator(result=result)
    controller = ChatController(mediator)
    app.include_router(controller.router, prefix="/chats")

    response = client.request(verb.upper(), f"/chats{path}", json=payload)
    assert response.status_code == expected_status
    assert response.json() == result
    assert isinstance(mediator.sent[0], cmd_class)


@pytest.mark.parametrize(
    "cmd_class,verb,path,payload",
    [
        (CreateChatCommand, "post", "/", {"title": "new"}),
        (
            UpdateChatTitleCommand,
            "patch",
            "/title",
            {"chat_id": str(uuid4()), "title": "upd"},
        ),
        (DeleteChatCommand, "delete", "/", {"chat_id": str(uuid4())}),
    ],
)
def test_commands_value_error(app, client, cmd_class, verb, path, payload):
    mediator = DummyMediator(exc=ValueError("error"))
    controller = ChatController(mediator)
    app.include_router(controller.router, prefix="/chats")

    response = client.request(verb.upper(), f"/chats{path}", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "error"
    assert isinstance(mediator.sent[0], cmd_class)
