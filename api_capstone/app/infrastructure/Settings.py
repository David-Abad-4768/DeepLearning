from dotenv import load_dotenv
from pydantic import ValidationError
from pydantic_settings import BaseSettings

from app.core.utils.Logger import get_logger

load_dotenv()
logger = get_logger(__name__)


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        extra = "ignore"


try:
    settings = Settings()
except ValidationError as e:
    logger.error("Error loading settings: %s", e.json())
    raise
