from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = (
        'postgresql+psycopg://alvo_user:alvo_password@localhost:5434/alvo_db'
    )

    SOURCE_API_URL: str = 'http://localhost:8000/api/v1'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
