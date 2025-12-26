from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = (
        'postgresql+psycopg://fonte_user:fonte_password@localhost:5432/fonte_db'
    )

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
