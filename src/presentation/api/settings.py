from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv(".env"))
env_file = find_dotenv(".env")


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_SYNC(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TEST_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}" \
               f"/{self.TEST_DB_NAME}"

    @property
    def TEST_DATABASE_URL_SYNC(self):
        return f"postgresql+psycopg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}" \
               f"/{self.TEST_DB_NAME}"


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int


class RabbitConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

    RABBIT_HOST: str
    RABBIT_PORT: int
    RABBIT_USER: str
    RABBIT_PASS: str


class EmailConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

    EMAIL_USER: str
    EMAIL_HOST: str
    EMAIL_PASSWORD: str
    EMAIL_PORT: int


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int


class OtherServiceConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

    SCHEDULE_SERVICE_HOST: str
    SCHEDULE_SERVICE_PORT: str
    USER_SERVICE_HOST: str
    USER_SERVICE_PORT: str
    ORDER_SERVICE_HOST: str
    ORDER_SERVICE_PORT: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

    MODE: Literal["DEV", "TEST", "PROD"]
    # LOG_LEVEL: str
    db: DatabaseConfig = DatabaseConfig()
    other_service_config: OtherServiceConfig = OtherServiceConfig()
    redis: RedisConfig = RedisConfig()
    email: EmailConfig = EmailConfig()
    auth: AuthConfig = AuthConfig()
    rabbit: RabbitConfig = RabbitConfig()

    # model_config = SettingsConfigDict(env_file=".env.docker")
    # model_config = SettingsConfigDict()


settings = Settings()
