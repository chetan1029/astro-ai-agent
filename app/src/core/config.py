from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Dict, List


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
    database_url: str
    whatsapp_verify_token: str
    whatsapp_access_token: str
    whatsapp_phone_number_id: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str
    whatsapp_provider: str  # twilio, cloud

    # Pub/Sub config
    pubsub_project_id: str
    topic_birth_profile: str
    sub_astro_profile: str
    topic_astro_profile: str
    sub_interpretation: str
    sub_horoscope: str
    topic_message_delivery: str
    sub_whatsapp_delivery: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def topic_sub_mapping(self) -> Dict[str, List[str]]:
        return {
            self.topic_birth_profile: [self.sub_astro_profile],
            self.topic_astro_profile: [self.sub_interpretation, self.sub_horoscope],
            self.topic_message_delivery: [self.sub_whatsapp_delivery],
        }

    @property
    def anyllm_model_url(self) -> str:
        return f"{self.anyllm_provider}/{self.anyllm_model}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
