import pytest
from fastapi import FastAPI, HTTPException, status
from starlette.testclient import TestClient

from app.application.commands.user.create.CreateUserCommand import \
    CreateCommand
from app.infrastructure.controllers.UserController import UserController


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
    application = FastAPI()
    return application


@pytest.fixture
def client(app):
    from uuid import uuid4

    user_id = str(uuid4())
    mediator = DummyMediator(
        result={
            "user": {
                "user_id": user_id,
                "username": "testuser",
                "email": "a@b.com",
                "password": "pwd",
            },
            "message": "User created",
        }
    )
    controller = UserController(mediator)
    app.include_router(controller.router, prefix="/users")
    return TestClient(app), mediator, user_id


def test_create_user_success(client):
    test_client, mediator, user_id = client
    payload = {"username": "testuser", "email": "a@b.com", "password": "pwd"}
    response = test_client.post("/users/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user"]["username"] == "testuser"
    assert data["user"]["user_id"] == user_id
    assert isinstance(mediator.sent[0], CreateCommand)


def test_create_user_value_error(client):
    test_client, mediator, user_id = client
    mediator.exc = ValueError("username exists")
    payload = {"username": "dup", "email": "a@b.com", "password": "pwd"}
    response = test_client.post("/users/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "username exists"
