import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.repositories.BaseRepository import BaseRepository

BaseTest = declarative_base()


class Dummy(BaseTest):
    __tablename__ = "dummies"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    BaseTest.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def repo(db_session: Session):
    return BaseRepository(Dummy, db_session)


def test_get_all_empty(repo):
    assert repo.get_all() == []
    with pytest.raises(ValueError):
        repo.get(1)


def test_create_and_get(repo):
    dummy = Dummy(name="foo")
    created = repo.create(dummy)
    assert created.id is not None
    fetched = repo.get(created.id)
    assert fetched.name == "foo"


def test_create_duplicate_raises(repo):
    d1 = Dummy(name="dup")
    repo.create(d1)
    d2 = Dummy(name="dup")
    with pytest.raises(ValueError) as exc:
        repo.create(d2)
    msg = str(exc.value)
    assert "Duplicate entry for name" in msg
    assert "in dummies" in msg


def test_create_many(repo):
    d1 = Dummy(name="a")
    d2 = Dummy(name="b")
    created = repo.create_many([d1, d2])
    assert len(created) == 2
    assert {o.name for o in created} == {"a", "b"}


def test_update(repo):
    d = Dummy(name="orig")
    repo.create(d)
    d.name = "changed"
    updated = repo.update(d)
    assert updated.name == "changed"


def test_delete(repo):
    d = Dummy(name="todelete")
    created = repo.create(d)
    repo.delete(created.id)
    with pytest.raises(ValueError):
        repo.get(created.id)


def test_refresh_db_after_integrity_error(repo, db_session, monkeypatch):
    d = Dummy(name="x1")
    repo.create(d)
    d.name = None

    class FakeOrig:
        def __str__(self):
            return "(sqlite3.IntegrityError) NOT NULL constraint failed: dummies.name"

    err = IntegrityError(statement=None, params=None, orig=FakeOrig())
    monkeypatch.setattr(db_session, "merge", lambda obj: (_ for _ in ()).throw(err))

    with pytest.raises(ValueError) as exc:
        repo.update(d)
    assert "Duplicate entry for name in dummies" in str(exc.value)


def test_parse_integrity_error_formatting():
    class FakeOrig:
        def __str__(self):
            return "(MySQLSyntaxError) Duplicate entry 'val' for key 'dummies.name'"

    err = IntegrityError(statement=None, params=None, orig=FakeOrig())
    msg = BaseRepository._parse_integrity_error(err)
    assert "Duplicate entry for name'" in msg
    assert "(MySQLSyntaxError)" in msg
    assert "Duplicate entry 'val' for key 'dummies." in msg
    assert "Choose another value." in msg


def test_get_all_multiple(repo):
    names = ["alpha", "beta", "gamma"]
    for n in names:
        repo.create(Dummy(name=n))
    all_objs = repo.get_all()
    assert {o.name for o in all_objs} == set(names)


def test_delete_nonexistent_raises(repo):
    with pytest.raises(ValueError) as exc:
        repo.delete(9999)
    assert "not found" in str(exc.value).lower()


def test_create_many_with_existing_duplicate_raises(repo):
    repo.create(Dummy(name="exists"))
    to_create = [Dummy(name="exists"), Dummy(name="new")]
    with pytest.raises(ValueError) as excinfo:
        repo.create_many(to_create)
    assert "Duplicate entry for name" in str(excinfo.value)
    assert "in dummies" in str(excinfo.value)
