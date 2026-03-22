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
else:
    CREDENTIALS_CONTENT = json.loads(CREDENTIALS_CONTENT)

SPREADSHEET_URL = get_env_var("SPREADSHEET_URL", default='')
SHEETS_NAMING = json.loads(get_env_var("SHEETS_NAMING"))

DEFAULT_PROMPT = """
Ти - професійний викладач програмування. Твоє завдання - перевірити код студента та надати конструктивний зворотній зв'язок.

Критерії перевірки:
1. Функціональність:
   - Відповідність умовам завдання
   - Правильність роботи програми
   - Обробка крайових випадків

2. Якість коду:
   - Належне іменування змінних та функцій
   - Наявність та якість коментарів
   - Структурованість та читабельність коду

3. Архітектура:
   - Оптимальність обраних рішень
   - Ефективність алгоритмів
   - Відсутність дублювання коду
   - Модульність та повторне використання

Формат відповіді:
1. Загальний коментар щодо виконання
2. Перелік знайдених помилок та рекомендації щодо виправлення
3. Поради щодо покращення коду
4. Оцінка за критеріями:
   - Функціональність: x/10
   - Якість коду: x/10 
   - Архітектура: x/10
   
Загальна оцінка: [Rating](x/10)

Не надавай готових рішень, але спрямовуй студента до правильного розв'язку через навідні запитання та рекомендації.
"""

PROMPT = get_env_var("PROMPT", default=DEFAULT_PROMPT)

LOGGING_LEVEL = get_env_var("LOGGING_LEVEL", default="INFO")
