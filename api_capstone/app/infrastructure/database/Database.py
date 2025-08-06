from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.infrastructure.Settings import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.domain.entities.Chat import ChatEntity
    from app.domain.entities.Message import MessageEntity
    from app.domain.entities.User import UserEntity

    Base.metadata.create_all(bind=engine)
