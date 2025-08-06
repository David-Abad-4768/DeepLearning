import pytest
from fastapi import Depends, FastAPI, HTTPException, status
from starlette.testclient import TestClient

from app.domain.entities.User import UserEntity
from app.infrastructure.controllers.AuthController import (AuthController,
                                                           auth_service)
from app.infrastructure.dependencies.Dependencies import get_current_user


@pytest.fixture
def app():
    app = FastAPI()
    controller = AuthController()
    app.include_router(controller.router, prefix="/auth")
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_login_success(client, monkeypatch):
    def fake_login(username, password, response):
        response.set_cookie(key="access_token", value="token123")

    monkeypatch.setattr(auth_service, "login_and_set_cookie", fake_login)
    payload = {"username": "user", "password": "pass"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Login successful"}
    assert response.cookies.get("access_token") == "token123"


def test_login_bad_credentials(client, monkeypatch):
    def fake_login(username, password, response):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad creds"
        )

    monkeypatch.setattr(auth_service, "login_and_set_cookie", fake_login)
    payload = {"username": "user", "password": "wrong"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Bad creds"


def test_login_server_error(client, monkeypatch):
    def fake_login(username, password, response):
        raise Exception("db fail")

    monkeypatch.setattr(auth_service, "login_and_set_cookie", fake_login)
    payload = {"username": "user", "password": "pass"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Internal server error"


def test_logout_success(client, monkeypatch):
    dummy_user = UserEntity(username="u")
    dummy_user.user_id = "id123"
    monkeypatch.setenv
    client.app.dependency_overrides[get_current_user] = lambda: dummy_user

    def fake_logout(response):
        response.delete_cookie(key="access_token")

    monkeypatch.setattr(auth_service, "logout_and_clear_cookie", fake_logout)
    response = client.post("/auth/logout")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Logout successful"}
    assert "access_token" not in response.cookies


def test_verify_success(client, monkeypatch):
    dummy_user = UserEntity(username="u")
    dummy_user.user_id = "id123"
    client.app.dependency_overrides[get_current_user] = lambda: dummy_user
    payload = {"sub": "id123"}
    monkeypatch.setattr(auth_service, "verify_token_cookie", lambda req: payload)
    response = client.get("/auth/verify")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"valid": True, "payload": payload}


def test_protected_routes_unauthorized(client, monkeypatch):
    client.app.dependency_overrides[get_current_user] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No auth")
    )
    resp_logout = client.post("/auth/logout")
    assert resp_logout.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp_logout.json()["detail"] == "No auth"
    resp_verify = client.get("/auth/verify")
    assert resp_verify.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp_verify.json()["detail"] == "No auth"
