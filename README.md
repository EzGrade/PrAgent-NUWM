# PullRequest Agent для НУВГП

## Опис

PullRequest Agent для НУВГП - це програма, яка дозволяє автоматизувати процес перевірки Pull Request'ів на відповідність
вимогам до коду в репозиторії НУВГП.
Бот використовує OpenAI API для аналізу коду та надає відповідь опираючись на промпт та код репозиторію.

## Встановлення

1. Створіть наступні змінні в https://github.com/organizations/<НАЗВА_ОРГАНІЗАЦІЇ>/settings/secrets/actions
    - `APP_ID` - ідентифікатор GitHub App(запитайте у власника репозиторію)
    - `OPENAI_API_KEY` - ключ для OpenAI API
    - `OPENAI_MODEL` - модель для OpenAI API
    - `PRIVATE_KEY` - персональний токен для доступу до бота(запитайте у власника репозиторію)
2. Створіть теку .github/workflows в корені вашого репозиторію.
3. Створіть файл pull_request_agent.yml(або інша назва) в щойно створеній теці .github/workflows.
4. Додайте наступний код в файл pull_request_agent.yml:

```yaml
name: PR Agent for NUWM

on:
  pull_request:
    types: [ opened, edited, synchronize ]

jobs:
  pr_agent_job:
    runs-on: ubuntu-latest
    name: Run pr agent on every pull request
    steps:
      - name: pr-agent-nuwm
        uses: EzGrade/Pr-Agent-NUWM@main
        env:
          APP_ID: ${{ secrets.APP_ID }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          PRIVATE_KEY: ${{ secrets.PRIVATE_KEY }}
          OPENAI_MODEL: ${{ secrets.OPENAI_MODEL }}
          INSTALLATION_ID: ${{ secrets.INSTALLATION_ID }}
```

5. Збережіть файл pull_request_agent.yml.

Після цього бот буде автоматично перевіряти Pull Request'и на відповідність вимогам до коду в репозиторії НУВГП.

### Для контакту з розробником звертайтесь в телеграм @JustGrade.
