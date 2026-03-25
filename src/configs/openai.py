from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .base import BaseApplicationConfig


class OpenAIConfig(BaseApplicationConfig):
    API_KEY: str = Field(..., description="OpenAI API Key")
    MODEL: str = Field(..., description="OpenAI Model")

    model_config = SettingsConfigDict(
        env_prefix="OPENAI_"
    )
