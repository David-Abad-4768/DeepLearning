import sqlalchemy

from app.core.Base import Base


def test_base_declarative_mapping():
    assert isinstance(Base, type)

    class TestModel(Base):
        __tablename__ = "test_model"
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    assert TestModel.__tablename__ == "test_model"

    mapper = sqlalchemy.inspect(TestModel)
    assert mapper is not None
    assert mapper.local_table.name == "test_model"
