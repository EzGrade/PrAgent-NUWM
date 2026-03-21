"""
This module contains configuration variables for the application.
"""

from utils.environment import get_env_var
import json

GITHUB_PRIVATE_KEY = get_env_var("PRIVATE_KEY")
GITHUB_APP_ID = int(get_env_var("APP_ID"))
if GITHUB_PRIVATE_KEY.endswith(".pem"):
    with open(GITHUB_PRIVATE_KEY, "r", encoding="utf-8") as key_file:
        GITHUB_PRIVATE_KEY = key_file.read()
GITHUB_INSTALLATION_ID = get_env_var("INSTALLATION_ID", default=None)

GITHUB_REPOSITORY = get_env_var("GITHUB_REPOSITORY").split("/")
GITHUB_REPOSITORY_OWNER = GITHUB_REPOSITORY[0]
GITHUB_REPOSITORY_NAME = GITHUB_REPOSITORY[1]

OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
OPENAI_MODEL = get_env_var("OPENAI_MODEL")

CREDENTIALS_CONTENT = get_env_var("GOOGLE_CREDENTIALS_CONTENT", default='')
if CREDENTIALS_CONTENT.endswith(".json"):
    with open(CREDENTIALS_CONTENT, "r", encoding="utf-8") as credentials_file:
        CREDENTIALS_CONTENT = json.loads(credentials_file.read())

SPREADSHEET_URL = get_env_var("SPREADSHEET_URL", default='')
SHEETS_NAMING = json.loads(get_env_var("SHEETS_NAMING"))

DEFAULT_PROMPT = """Ти вчитель, твоя задача перевірити завдання учня.
Не давай готового коду, але можеш допомогти зрозуміти помилки.
Перевір код на дотримання форматування та конвенцій.
"""

PROMPT = get_env_var("PROMPT", default=DEFAULT_PROMPT)

LOGGING_LEVEL = get_env_var("LOGGING_LEVEL", default="INFO")
