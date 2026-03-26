from pydantic import Field, model_validator, field_validator, AliasChoices
from pydantic_settings import SettingsConfigDict

from .base import BaseApplicationConfig


class GitHubConfig(BaseApplicationConfig):
    APP_ID: int = Field(
        ..., 
        description="GitHub App ID",
        validation_alias=AliasChoices("GIT_APP_ID", "APP_ID")
    )
    INSTALLATION_ID: int | None = Field(
        default=None, 
        description="GitHub Installation ID",
        validation_alias=AliasChoices("GIT_INSTALLATION_ID", "INSTALLATION_ID")
    )
    REPOSITORY: str = Field(
        ..., 
        description="GitHub Repository",
        validation_alias=AliasChoices("GIT_REPOSITORY", "GITHUB_REPOSITORY")
    )
    PRIVATE_KEY: str = Field(
        ..., 
        description="GitHub Private Key",
        validation_alias=AliasChoices("GIT_PRIVATE_KEY", "PRIVATE_KEY")
    )

    model_config = SettingsConfigDict(
        env_prefix=""  # Без префіксу, бо використовуємо AliasChoices
    )

    @field_validator("INSTALLATION_ID", mode="before")
    @classmethod
    def validate_installation_id(cls, value):
        """Конвертуємо порожній рядок в None для INSTALLATION_ID"""
        if value == "" or value is None:
            return None
        return value

    @field_validator("APP_ID", mode="before")
    @classmethod
    def validate_app_id(cls, value):
        """Перевіряємо, що APP_ID не порожній"""
        if value == "":
            raise ValueError(
                "APP_ID cannot be empty. Please set the GIT_APP_ID secret in your organization settings. "
                "Go to https://github.com/organizations/nuwm-lab/settings/secrets/actions"
            )
        return value

    @field_validator("PRIVATE_KEY", mode="before")
    @classmethod
    def validate_private_key_empty(cls, value):
        """Перевіряємо, що PRIVATE_KEY не порожній"""
        if value == "":
            raise ValueError(
                "PRIVATE_KEY cannot be empty. Please set the GIT_PRIVATE_KEY secret in your organization settings. "
                "Go to https://github.com/organizations/nuwm-lab/settings/secrets/actions"
            )
        return value

    @model_validator(mode="after")
    def load_private_key(self):
        if self.PRIVATE_KEY.endswith(".pem"):
            with open(self.PRIVATE_KEY, "r", encoding="utf-8") as private_key_file:
                self.PRIVATE_KEY = private_key_file.read()

        return self
