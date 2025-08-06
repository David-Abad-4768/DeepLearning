from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.requests import Request
from starlette.datastructures import MutableHeaders

from app.domain.entities.User import UserEntity
from app.infrastructure.dependencies.Dependencies import (auth_service,
                                                          get_current_user)
from app.infrastructure.repositories.UserRepository import UserRepository


class DummySession:
    def __init__(self, user=None):
        self._user = user

    def query(self, model):
        class Q:
            def __init__(self, user):
                self.user = user

            def filter(self, *args, **kwargs):
                return self

            def first(self):
                return self.user

        return Q(self._user)

    def close(self):
        pass


class DummyRequest:
    def __init__(self, token=None):
        self.cookies = {"access_token": token} if token is not None else {}


@pytest.fixture(autouse=True)
def reset_monkeypatch(monkeypatch):
    monkeypatch.setattr(
        "app.infrastructure.dependencies.Dependencies.SessionLocal",
        lambda: DummySession(),
    )
    yield


def test_no_cookie_raises(monkeypatch):
    req = DummyRequest()
    with pytest.raises(HTTPException) as exc:
        get_current_user(req)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


@pytest.fixture
def valid_token(monkeypatch):
    user_id = str(uuid4())
    payload = {"sub": user_id}
    monkeypatch.setattr(auth_service, "decode_token", lambda t: payload)
    return user_id


def test_invalid_payload_missing_sub(monkeypatch):
    token = "tok"
    monkeypatch.setattr(auth_service, "decode_token", lambda t: {})
    req = DummyRequest(token)
    with pytest.raises(HTTPException) as exc:
        get_current_user(req)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token payload"


def test_invalid_uuid_in_payload(monkeypatch, valid_token):
    token = "tok"
    monkeypatch.setattr(auth_service, "decode_token", lambda t: {"sub": "not-uuid"})
    req = DummyRequest(token)
    with pytest.raises(HTTPException) as exc:
        get_current_user(req)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid user ID in token"
