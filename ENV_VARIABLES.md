# 🎯 Quick Reference: Environment Variables

## Supported Formats

The bot supports **BOTH** naming conventions for maximum compatibility!

### ✅ Option 1: With Prefixes (Recommended for clarity)
```yaml
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
```

### ✅ Option 2: Without Prefixes (Legacy support)
```yaml
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
```

## Variable Aliases

| Config Group | With Prefix | Without Prefix |
|-------------|-------------|----------------|
| **GitHub** | `GIT_APP_ID` | `APP_ID` |
| | `GIT_PRIVATE_KEY` | `PRIVATE_KEY` |
| | `GIT_INSTALLATION_ID` | `INSTALLATION_ID` |
| | `GIT_REPOSITORY` | `GITHUB_REPOSITORY` |
| **OpenAI** | `OPENAI_API_KEY` | `API_KEY` |
| | `OPENAI_MODEL` | `MODEL` |
| **Google** | `GOOGLE_CREDENTIALS_CONTENT` | `CREDENTIALS_CONTENT` |
| | `GOOGLE_SPREADSHEET_URL` | `SPREADSHEET_URL` |
| | `GOOGLE_SHEETS_NAMING` | `SHEETS_NAMING` |

## 🔥 No Migration Needed!

Existing workflows in student repositories will continue to work without any changes!
