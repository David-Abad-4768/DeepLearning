# tests/application/services/test_AuthService.py

from datetime import timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError
from starlette.responses import Response

from app.application.services.AuthService import AuthService
from app.infrastructure.Settings import settings


class FakeUser:
    def __init__(self, user_id, password_hash):
        self.user_id = user_id
        self.password = password_hash


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch):
    monkeypatch.setattr(settings, "secret_key", "testsecret")
    monkeypatch.setattr(settings, "algorithm", "HS256")
    yield


def test_hash_and_verify_password():
    svc = AuthService()
    plain = "mypassword"
    h = svc.hash_password(plain)
    assert h != plain
    assert svc._verify_password(plain, h)
    assert not svc._verify_password("wrong", h)


def test_create_and_decode_token():
    svc = AuthService()
    data = {"sub": "subject"}
    token = svc.create_access_token(data, expires_delta=timedelta(seconds=60))
    decoded = svc.decode_token(token)
    assert decoded["sub"] == "subject"
    assert "exp" in decoded


def test_decode_token_expired(monkeypatch):
    svc = AuthService()
    import jose.jwt as jose_jwt

    monkeypatch.setattr(
        jose_jwt,
        "decode",
        lambda *args, **kwargs: (_ for _ in ()).throw(ExpiredSignatureError()),
    )
    with pytest.raises(HTTPException) as exc:
        svc.decode_token("anytoken")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "expired" in exc.value.detail.lower()


def test_decode_token_invalid(monkeypatch):
    svc = AuthService()
    import jose.jwt as jose_jwt

    monkeypatch.setattr(
        jose_jwt, "decode", lambda *args, **kwargs: (_ for _ in ()).throw(JWTError())
    )
    with pytest.raises(HTTPException) as exc:
        svc.decode_token("anytoken")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in exc.value.detail.lower()


def test_login_and_set_cookie_success(monkeypatch):
    svc = AuthService()
    fake = FakeUser(user_id="uid123", password_hash=svc.hash_password("pass"))
    monkeypatch.setattr(svc, "authenticate_user", lambda u, p: fake)
    resp = Response()
    user, token = svc.login_and_set_cookie(
        "u", "p", resp, token_name="tok", expires_delta=timedelta(minutes=5)
    )
    assert user is fake
    assert isinstance(token, str)
    cookies = resp.raw_headers
    assert any(b"tok=" in val for _, val in cookies)


def test_login_and_set_cookie_failure(monkeypatch):
    svc = AuthService()
    monkeypatch.setattr(svc, "authenticate_user", lambda u, p: None)
    resp = Response()
    with pytest.raises(HTTPException) as exc:
        svc.login_and_set_cookie("u", "p", resp)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid username or password" in exc.value.detail.lower()


def test_logout_and_clear_cookie():
    svc = AuthService()
    resp = Response()
    resp.set_cookie(key="tok", value="v")
    svc.logout_and_clear_cookie(resp, token_name="tok")
    # header value cleared
    assert any(b"tok=" in val for _, val in resp.raw_headers)


def test_verify_token_cookie_success():
    svc = AuthService()
    token = svc.create_access_token({"sub": "x"})
    req = SimpleNamespace(cookies={"access_token": token})
    data = svc.verify_token_cookie(req)
    assert data["sub"] == "x"


def test_verify_token_cookie_missing():
    svc = AuthService()
    req = SimpleNamespace(cookies={})
    with pytest.raises(HTTPException) as exc:
        svc.verify_token_cookie(req)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "not found" in exc.value.detail.lower()
