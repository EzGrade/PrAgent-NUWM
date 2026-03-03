from utils.environment import get_env_var

GITHUB_PRIVATE_KEY = get_env_var("PRIVATE_KEY")
GITHUB_APP_ID = int(get_env_var("APP_ID"))
if GITHUB_PRIVATE_KEY.endswith(".pem"):
    GITHUB_PRIVATE_KEY = open(GITHUB_PRIVATE_KEY, "r").read()

OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
OPENAI_MODEL = get_env_var("OPENAI_MODEL")

default_prompt = """You are a teacher reviewing a student's code.
You should give only advices, not complete code.
Check code for different conventions, and give advices about best practices.
Send response in format for leaving comment to pull request.
Use markup as it will be posted on GitHub.
It will be posted on github, so use markups inside body
The student has submitted the following files for review:"""

PROMPT = get_env_var("PROMPT", default=default_prompt)
