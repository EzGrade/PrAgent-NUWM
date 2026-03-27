from pydantic import Field, AliasChoices
from pydantic_settings import SettingsConfigDict

from .base import BaseApplicationConfig


class OpenAIConfig(BaseApplicationConfig):
    API_KEY: str = Field(
        ..., 
        description="OpenAI API Key",
        validation_alias=AliasChoices("OPENAI_API_KEY", "API_KEY")
    )
    MODEL: str = Field(
        ..., 
        description="OpenAI Model",
        validation_alias=AliasChoices("OPENAI_MODEL", "MODEL")
    )

    model_config = SettingsConfigDict(
        env_prefix=""  # Без префіксу, бо використовуємо AliasChoices
    )
