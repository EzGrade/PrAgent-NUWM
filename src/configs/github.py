from pydantic import Field, model_validator, AliasChoices
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

    @model_validator(mode="before")
    def validate_fields(cls, values):
        # Перевіряємо INSTALLATION_ID
        installation_id = values.get("INSTALLATION_ID")
        if not installation_id or installation_id == "":
            values["INSTALLATION_ID"] = None

        # Перевіряємо APP_ID - не може бути порожнім
        app_id = values.get("APP_ID")
        if app_id == "":
            raise ValueError(
                "APP_ID cannot be empty. Please set the APP_ID secret in your repository settings. "
                "Go to Settings → Secrets and variables → Actions → Repository secrets"
            )

        # Перевіряємо PRIVATE_KEY - не може бути порожнім
        private_key = values.get("PRIVATE_KEY")
        if private_key == "":
            raise ValueError(
                "PRIVATE_KEY cannot be empty. Please set the PRIVATE_KEY secret in your repository settings. "
                "Go to Settings → Secrets and variables → Actions → Repository secrets"
            )

        return values

    @model_validator(mode="after")
    def load_private_key(self):
        if self.PRIVATE_KEY.endswith(".pem"):
            with open(self.PRIVATE_KEY, "r", encoding="utf-8") as private_key_file:
                self.PRIVATE_KEY = private_key_file.read()

        return self
