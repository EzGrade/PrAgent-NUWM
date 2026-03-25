from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseApplicationConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore",
        case_sensitive=False,
        env_file_encoding="utf-8",
    )
