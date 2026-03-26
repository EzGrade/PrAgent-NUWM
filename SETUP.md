# Інструкція з налаштування PR Agent для NUWM

## ✨ Особливість

Бот підтримує **обидва формати** змінних середовища для максимальної сумісності:
- ✅ **З префіксами**: `GIT_APP_ID`, `GOOGLE_SPREADSHEET_URL`, `OPENAI_API_KEY`
- ✅ **Без префіксів**: `APP_ID`, `SPREADSHEET_URL`, `API_KEY`

**Ви можете використовувати будь-який варіант!** Старі workflow файли продовжать працювати без змін.

---

## Налаштування для репозиторіів студентів

### 1. Створіть workflow файл

У репозиторії студента створіть файл `.github/workflows/review.yml`.

**Варіант А: З префіксами (рекомендовано для нових проектів)**

```yaml
name: PR Agent for NUWM

on:
  pull_request:
    types: [ opened, edited, synchronize, reopened ]

jobs:
  pr_agent_job:
    runs-on: ubuntu-latest
    name: Run pr agent on every pull request
    steps:
      - name: pr-agent-nuwm
        uses: EzGrade/Pr-Agent-NUWM@main
        env:
          GIT_APP_ID: ${{ secrets.APP_ID }}
          GIT_PRIVATE_KEY: ${{ secrets.PRIVATE_KEY }}
          GIT_INSTALLATION_ID: ${{ secrets.INSTALLATION_ID }}
          GIT_REPOSITORY: ${{ github.repository }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          OPENAI_MODEL: ${{ secrets.OPENAI_MODEL }}
          GOOGLE_CREDENTIALS_CONTENT: ${{ secrets.GOOGLE_CREDENTIALS_CONTENT }}
          GOOGLE_SPREADSHEET_URL: ${{ secrets.SPREADSHEET_URL }}
          GOOGLE_SHEETS_NAMING: ${{ secrets.SHEETS_NAMING }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Варіант Б: Без префіксів (підтримується для зворотної сумісності)**

```yaml
name: PR Agent for NUWM

on:
  pull_request:
    types: [ opened, reopened ]

jobs:
  pr_agent_job:
    runs-on: ubuntu-latest
    name: Run pr agent on every pull request
    steps:
      - name: pr-agent-nuwm
        uses: EzGrade/Pr-Agent-NUWM@main
        env:
          APP_ID: ${{ secrets.APP_ID }}
          PRIVATE_KEY: ${{ secrets.PRIVATE_KEY }}
          INSTALLATION_ID: ${{ secrets.INSTALLATION_ID }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          OPENAI_MODEL: ${{ secrets.OPENAI_MODEL }}
          GOOGLE_CREDENTIALS_CONTENT: ${{ secrets.GOOGLE_CREDENTIALS_CONTENT }}
          SPREADSHEET_URL: ${{ secrets.SPREADSHEET_URL }}
          SHEETS_NAMING: ${{ secrets.SHEETS_NAMING }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 2. Налаштуйте GitHub Secrets

У репозиторії (Settings → Secrets and variables → Actions) додайте наступні секрети:

#### GitHub App секрети:
- `APP_ID` - ID вашого GitHub App
- `PRIVATE_KEY` - Приватний ключ GitHub App
- `INSTALLATION_ID` - (опціонально) ID інсталяції

#### OpenAI секрети:
- `OPENAI_API_KEY` - API ключ OpenAI
- `OPENAI_MODEL` - Модель OpenAI (наприклад, `gpt-4`)

#### Google Sheets секрети:
- `GOOGLE_CREDENTIALS_CONTENT` - JSON з credentials для Google Sheets API
- `SPREADSHEET_URL` - URL таблиці Google Sheets
- `SHEETS_NAMING` - JSON з назвами аркушів

---

## Підтримувані варіанти назв змінних

Завдяки `AliasChoices`, **обидва** формати працюють:

### GitHub конфігурація:
| З префіксом | Без префікса | Опис |
|------------|--------------|------|
| `GIT_APP_ID` | `APP_ID` | GitHub App ID |
| `GIT_PRIVATE_KEY` | `PRIVATE_KEY` | Private Key |
| `GIT_INSTALLATION_ID` | `INSTALLATION_ID` | Installation ID (опціонально) |
| `GIT_REPOSITORY` | `GITHUB_REPOSITORY` | Назва репозиторію |

### Google Sheets конфігурація:
| З префіксом | Без префікса | Опис |
|------------|--------------|------|
| `GOOGLE_CREDENTIALS_CONTENT` | `CREDENTIALS_CONTENT` | Google Sheets credentials |
| `GOOGLE_SPREADSHEET_URL` | `SPREADSHEET_URL` | URL таблиці |
| `GOOGLE_SHEETS_NAMING` | `SHEETS_NAMING` | Назви аркушів |

### OpenAI конфігурація:
| З префіксом | Без префікса | Опис |
|------------|--------------|------|
| `OPENAI_API_KEY` | `API_KEY` | OpenAI API ключ |
| `OPENAI_MODEL` | `MODEL` | Назва моделі |

### Системні змінні:
- `GITHUB_TOKEN` - Автоматично надається GitHub Actions ✅

---

## Перевірка налаштувань

Після налаштування:

1. Створіть Pull Request в репозиторії студента
2. Перевірте вкладку "Actions" на GitHub
3. Подивіться логи виконання workflow
4. Переконайтеся, що немає помилок валідації Pydantic

---

## Troubleshooting

### Помилка: `Field required [type=missing]`
**Причина:** Не налаштовано обов'язковий secret  
**Рішення:** Додайте відсутній secret у Settings → Secrets and variables → Actions

### Помилка: `Installation not found`
**Причина:** GitHub App не встановлено в організації/репозиторії  
**Рішення:** Встановіть GitHub App або додайте правильний `INSTALLATION_ID`

### Помилка: `Error parsing credentials JSON`
**Причина:** Невалідний JSON у `GOOGLE_CREDENTIALS_CONTENT`  
**Рішення:** Перевірте формат JSON credentials файлу

---

## Підтримка

Якщо виникли питання або проблеми, створіть Issue в репозиторії `EzGrade/Pr-Agent-NUWM`.
