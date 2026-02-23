
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra='ignore')
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALG: str = 'HS256'
    ACCESS_TOKEN_MINUTES: int = 120
    CELERY_BROKER_URL: str = 'redis://redis:6379/1'
    CELERY_RESULT_BACKEND: str = 'redis://redis:6379/2'
    APP_CURRENCY: str = 'TRY'


settings = Settings()
