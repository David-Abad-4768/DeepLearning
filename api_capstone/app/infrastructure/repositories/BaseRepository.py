from typing import Generic, List, Type, TypeVar, Union
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure.database.Database import SessionLocal

T = TypeVar("T")
PK = Union[int, str, UUID]


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get(self, id_: PK) -> T:
        instance = self.db.get(self.model, id_)
        if instance is None:
            raise ValueError(f"{self.model.__name__} with id {id_} not found.")
        return instance

    def get_all(self) -> List[T]:
        return self.db.query(self.model).all()

    def create(self, obj: T) -> T:
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError as e:
            self.db.rollback()
            self._refresh_db()
            raise ValueError(self._parse_integrity_error(e)) from e

    def create_many(self, objs: List[T]) -> List[T]:
        try:
            self.db.add_all(objs)
            self.db.commit()
            for obj in objs:
                self.db.refresh(obj)
            return objs
        except IntegrityError as e:
            self.db.rollback()
            self._refresh_db()
            raise ValueError(self._parse_integrity_error(e)) from e

    def update(self, obj: T) -> T:
        try:
            updated = self.db.merge(obj)
            self.db.commit()
            return updated
        except IntegrityError as e:
            self.db.rollback()
            self._refresh_db()
            raise ValueError(self._parse_integrity_error(e)) from e

    def delete(self, id_: PK) -> None:
        inst = self.get(id_)
        self.db.delete(inst)
        self.db.commit()

    def _refresh_db(self):
        self.db.close()
        self.db = SessionLocal()

    @staticmethod
    def _parse_integrity_error(error: IntegrityError) -> str:
        msg = str(error.orig).split(":")[-1].replace("\n", "").strip()
        parts = msg.split(".")
        if len(parts) >= 2:
            table, column = parts[-2], parts[-1]
            return f"Duplicate entry for {column} in {table}. Choose another value."
        return "Integrity error while processing your request."
