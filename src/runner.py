"""
This is the main runner file that will be executed by the GitHub action.
"""
import pandas as pd
import logging

from config import GITHUB_REPOSITORY_OWNER, GITHUB_REPOSITORY_NAME
from services.ai.service import AiRequest
from services.git.service import GitHub
from services.google.service import GoogleSheet
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

        google_client = GoogleSheet()
        students_variant: pd.DataFrame = google_client.get_variants_sheet()
        students_roster: pd.DataFrame = google_client.get_roster_sheet()

        lab_name = git_client.get_lab_name(all_lab_names=google_client.get_all_lab_names())
        pr_creator = git_client.get_student(lab_name=lab_name)
        if pr_creator not in google_client.get_all_nicknames():
            logger.error(f"Student with nickname {pr_creator} not found in the roster sheet.")
            git_client.leave_comment_on_pr(comment="Будь ласка, підв'яжіть свій акаунт на GitHub classroom та зверніться до адміністатора для оновлення інформації. Дякую!", pull_number=git_client.get_last_pr_number())
            return False

        prompts = google_client.get_teacher_prompts(lab_name=lab_name)

        student = StudentVariant(
            student_username=pr_creator,
            readme_variants=files.get("README.md", ""),
            variants_sheet=students_variant,
            roster_sheet=students_roster
        )

        files.pop("README.md", None)

        prompt_client = PromptGenerator(
            student_assignment=student.student_assignment,
            context_prompt=files,
            teacher_prompts=prompts
        )

        context = prompt_client.get_prompt()

        ai_client = AiRequest(context=context)
        response = ai_client.get_response()

        git_client.leave_comment_on_pr(comment=response["comment"])

        google_client.leave_response(
            student_variant=student,
            student_name=student.student_real_name,
            sheet_name=lab_name,
            ai_response=response["comment"],
            last_pr_link=git_client.get_last_pr_link(),
            prompt=prompt_client.context,
            summary=response["rating"]
        )
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
