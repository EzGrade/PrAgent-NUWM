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
    def validate_installation_id(cls, values):
        if not values.get("INSTALLATION_ID"):
            values["INSTALLATION_ID"] = None

        return values

    @model_validator(mode="after")
    def load_private_key(self):
        if self.PRIVATE_KEY.endswith(".pem"):
            with open(self.PRIVATE_KEY, "r", encoding="utf-8") as private_key_file:
                self.PRIVATE_KEY = private_key_file.read()

        return self
