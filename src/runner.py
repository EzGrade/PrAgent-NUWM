from config import GITHUB_REPOSITORY_OWNER, GITHUB_REPOSITORY_NAME
from services import prompt, ai, git


def run(
        owner: str,
        repository: str
):
    git_client = git.service.GitHub(
        owner=owner,
        repo=repository
    )
    files = git_client.get_pr_files_content()

    prompt_client = prompt.service.PromptGenerator(
        system_prompt="System prompt",
        context_prompt=files
    )
    context = prompt_client.get_prompt()

    ai_client = ai.service.AiRequest(
        context=context
    )
    response = ai_client.get_response()

    comment_response = git_client.leave_comment_on_pr(
        comment=response
    )
    return True


if __name__ == "__main__":
    run(
        owner=GITHUB_REPOSITORY_OWNER,
        repository=GITHUB_REPOSITORY_NAME
    )
