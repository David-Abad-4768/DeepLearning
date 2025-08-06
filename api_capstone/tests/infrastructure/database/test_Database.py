import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.Base import Base as CoreBase
from app.domain.entities.User import UserEntity
from app.infrastructure.repositories.UserRepository import UserRepository


@pytest.fixture(autouse=True)
def reset_singleton():
    UserRepository._instance = None
    yield
    UserRepository._instance = None


@pytest.fixture
def session_factory(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    CoreBase.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    monkeypatch.setattr(
        "app.infrastructure.repositories.UserRepository.SessionLocal", TestSessionLocal
    )
    return TestSessionLocal


@pytest.fixture
def db_session(session_factory):
    return session_factory()


def test_instance_is_singleton():
    repo1 = UserRepository.instance()
    repo2 = UserRepository.instance()
    assert repo1 is repo2
    assert hasattr(repo1, "db")


def test_get_by_username_returns_none_if_not_found(db_session):
    repo = UserRepository(db_session)
    assert repo.get_by_username("no_existe") is None
