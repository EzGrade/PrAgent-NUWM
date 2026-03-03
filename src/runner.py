from services import git, ai, prompt


def run(
        owner: str,
        repository: str
):
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
    print(context)

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
        owner="PullPal-Tester",
        repository="PullTestRepo"
    )
