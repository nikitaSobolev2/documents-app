from pydantic_settings import BaseSettings, SettingsConfigDict


class CeleryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str


celery_config = CeleryConfig()
