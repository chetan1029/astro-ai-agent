from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str
    app_env: str
    admin_email: str
    app_token: str
    postgres_db: str
    database_host: str
    database_port: int = 5432
    postgres_user: str
    postgres_password: str
    google_api_key: str
    openai_api_key: str
    anyllm_provider: str
    anyllm_model: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.database_host}:{self.database_port}/{self.postgres_db}"

    @property
    def anyllm_model_url(self) -> str:
        return f"{self.anyllm_provider}/{self.anyllm_model}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
