import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV)

    project_name: str

    redis_host: str
    redis_port: int

    pg_user: str
    pg_password: str
    pg_host: str
    pg_port: int
    pg_db: str

    @property
    def redis_dsn(self):
        return f"redis://{self.redis_host}:{self.redis_port}"
    
    @property
    def database_dsn(self):
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_port}"


auth_settings = AuthSettings()
