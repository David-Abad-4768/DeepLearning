import importlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.Base import Base
from app.domain.entities.User import UserEntity

# registra dependencias de UserEntity → ChatEntity → MessageEntity
importlib.import_module("app.domain.entities.Chat")
importlib.import_module("app.domain.entities.Message")

engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(engine)


def test_user_entity_fields(db_session):
    user = UserEntity(
        username="testuser", email="testuser@example.com", password="securepassword123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert isinstance(user.user_id, str)
    assert uuid.UUID(user.user_id)
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    assert user.password == "securepassword123"


def test_user_entity_defaults(db_session):
    user = UserEntity(username="user2", email="user2@example.com", password="pass456")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.user_id is not None
    uuid_obj = uuid.UUID(user.user_id)
    assert str(uuid_obj) == user.user_id
