from json import loads

from pydantic import Field, model_validator
from pydantic_settings import SettingsConfigDict
from loguru import logger

from .base import BaseApplicationConfig
from ..utils.enums.sheets import SheetsNamingEnum


class GoogleSheetsConfig(BaseApplicationConfig):
    CREDENTIALS_CONTENT: str | dict = Field(..., description="Google credentials content")
    SPREADSHEET_URL: str = Field(..., description="Google Spreadsheet URL")
    SHEETS_NAMING: dict = Field(..., description="Google Sheets naming")

    model_config = SettingsConfigDict(
        env_prefix="GOOGLE_"
    )

    @model_validator(mode="before")
    def load_credentials(cls, values):
        credentials = values.get("CREDENTIALS_CONTENT")
        if isinstance(credentials, str):
            if credentials.endswith(".json"):
                with open(credentials, "r", encoding="utf-8") as credentials_file:
                    content = credentials_file.read()
                    values["CREDENTIALS_CONTENT"] = loads(content)
                    logger.info("Credentials loaded from file")
            else:
                try:
                    values["CREDENTIALS_CONTENT"] = loads(credentials)
                except Exception as e:
                    logger.error(f"Error parsing credentials JSON: {e}")
                    raise
        return values

    def get_sheet_name(self, key: SheetsNamingEnum) -> str:
        name = self.SHEETS_NAMING.get(key.value, None)
        if name is None:
            raise ValueError(f"Sheet name for {key} not found")
        return name
