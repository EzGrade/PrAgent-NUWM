"""
This is the main runner file that will be executed by the GitHub action.
"""

from config import GITHUB_REPOSITORY_OWNER, GITHUB_REPOSITORY_NAME
from services import git, ai, prompt


def run(
        owner: str,
        repository: str
):
    """
    This function is the main entry point for the application.
    :param owner:
    :param repository:
    :return:
    """
    git_client = git.GitHub(
        owner=owner,
        repo=repository
    )
    files = git_client.get_pr_files_content()

    prompt_client = prompt.PromptGenerator(
        system_prompt="System prompt",
        context_prompt=files
    )
    context = prompt_client.get_prompt()

    ai_client = ai.AiRequest(
        context=context
    )
    response = ai_client.get_response()

    git_client.leave_comment_on_pr(
        comment=response
    )
    return True


if __name__ == "__main__":
    run(
        owner=GITHUB_REPOSITORY_OWNER,
        repository=GITHUB_REPOSITORY_NAME
    )
