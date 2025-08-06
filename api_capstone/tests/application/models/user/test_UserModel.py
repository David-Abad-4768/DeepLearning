from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.application.models.user.UserModel import (CreateModel, CreateResponse,
                                                   DeleteModel, DeleteResponse,
                                                   Token, TokenData, User)


def test_token_model_valid_and_missing_fields():
    t = Token(access_token="abc", token_type="bearer")
    assert t.access_token == "abc"
    assert t.token_type == "bearer"
    with pytest.raises(ValidationError):
        Token(token_type="bearer")
    with pytest.raises(ValidationError):
        Token(access_token="abc")


def test_token_data_optional_username():
    td1 = TokenData()
    assert td1.username is None
    td2 = TokenData(username="user1")
    assert td2.username == "user1"


def test_user_model_valid_and_invalid():
    uid = uuid4()
    u = User(user_id=uid, username="joe", email="joe@example.com", password="pw")
    assert isinstance(u.user_id, UUID)
    assert u.username == "joe"
    assert u.email == "joe@example.com"
    assert u.password == "pw"
    with pytest.raises(ValidationError):
        User(username="joe", email="joe@example.com", password=None)
    with pytest.raises(ValidationError):
        User(user_id=uid, username="joe", password="pw")
    with pytest.raises(ValidationError):
        User(username="joe", email="not-an-email", password="pw")


def test_create_model_valid_and_missing_fields():
    cm = CreateModel(username="u", email="u@example.com", password="p")
    assert cm.username == "u"
    assert cm.email == "u@example.com"
    assert cm.password == "p"
    with pytest.raises(ValidationError):
        CreateModel(email="u@example.com", password="p")
    with pytest.raises(ValidationError):
        CreateModel(username="u", password="p")
    with pytest.raises(ValidationError):
        CreateModel(username="u", email="x", password="p")


def test_create_response_valid_and_missing_fields():
    uid = uuid4()
    user = User(user_id=uid, username="u", email="u@example.com", password="pw")
    cr = CreateResponse(user=user, message="created")
    assert cr.user is user
    assert cr.message == "created"
    with pytest.raises(ValidationError):
        CreateResponse(message="created")
    with pytest.raises(ValidationError):
        CreateResponse(user=user)


def test_delete_model_valid_and_missing_fields():
    uid = uuid4()
    dm = DeleteModel(user_id=uid)
    assert dm.user_id == uid
    with pytest.raises(ValidationError):
        DeleteModel()


def test_delete_response_valid_and_missing_fields():
    dr = DeleteResponse(message="gone")
    assert dr.message == "gone"
    with pytest.raises(ValidationError):
        DeleteResponse()
