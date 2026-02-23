from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.system import AppEnv


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    APP_NAME: str
    APP_URL: str
    APP_ENV: AppEnv
    DATABASE_URL: str
    REDIS_URL: str


config = Config()
