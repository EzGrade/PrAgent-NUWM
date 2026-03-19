"""
This is the main runner file that will be executed by the GitHub action.
"""
import pandas as pd
import logging

from config import GITHUB_REPOSITORY_OWNER, GITHUB_REPOSITORY_NAME
from services.ai.service import AiRequest
from services.git.service import GitHub
from services.prompt.service import PromptGenerator
from services.student_variant.service import StudentVariant
from utils.logger import setup_logger

logger = setup_logger(__name__, level=logging.DEBUG)


def run(owner: str, repository: str) -> bool:
    """
    This function is the main entry point for the application.
    :param owner: GitHub repository owner
    :param repository: GitHub repository name
    :return: True if the process completes successfully, False otherwise
    """
    try:
        git_client = GitHub(owner=owner, repo=repository)
        files = git_client.get_pr_files_content()
        pr_creator = git_client.get_pr_creator()
        roaster_path = ""
        if roaster_path == "":
            raise ValueError("Roaster path is not set")
        with open(roaster_path) as file:
            roaster = pd.read_csv(file)

        student_variant = StudentVariant(
            student_username=pr_creator,
            readme_variants=files.get("README.md", ""),
            csv_roaster=roaster
        )
        files.pop("README.md", None)

        prompt_client = PromptGenerator(
            system_prompt="System prompt",
            student_assignment=student_variant.map_student_to_variant(),
            context_prompt=files
        )
        context = prompt_client.get_prompt()

        ai_client = AiRequest(context=context)
        response = ai_client.get_response()

        git_client.leave_comment_on_pr(comment=response)
        return True

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False


if __name__ == "__main__":
    success = run(owner=GITHUB_REPOSITORY_OWNER, repository=GITHUB_REPOSITORY_NAME)
    if success:
        logger.info("Process completed successfully.")
    else:
        logger.error("Process failed.")
