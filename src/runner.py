"""
This is the main runner file that will be executed by the GitHub action.
"""
import os
import pandas as pd
from loguru import logger

from services.ai.service import AiRequest
from services.git.service import GitHub
from services.google.service import GoogleSheet
from services.prompt.service import PromptGenerator
from services.student_variant.service import StudentVariant
from models.llm.tools import ReviewCodeTool


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
            git_client.comment_pr(
                comment="Будь ласка, підв'яжіть свій акаунт на GitHub classroom та зверніться до адміністатора для оновлення інформації. Дякую!",
                pull_number=git_client.get_last_pr_number())
            return False

        student = StudentVariant(
            student_username=pr_creator,
            readme_variants=files.get("README.md", ""),
            variants_sheet=students_variant,
            roster_sheet=students_roster
        )

        files.pop("README.md", None)

        lab_prompt = google_client.get_teacher_prompts(name=lab_name)

        prompt_service = PromptGenerator(
            student_assignment=student.student_assignment,
            context_prompt=files,
            teacher_prompts=lab_prompt
        )

        context = prompt_service.get_prompt()

        ai_client = AiRequest()
        response: ReviewCodeTool = ai_client.send_message(context=context)

        git_client.comment_pr(
            comment=response.message,
            pull_number=git_client.get_last_pr_number()
        )

        google_client.leave_response(
            student_variant=student,
            student_name=student.student_real_name,
            sheet_name=lab_name,
            ai_response=response.message,
            last_pr_link=git_client.get_last_pr_link(),
            prompt=prompt_service.context,
            summary=f"{response.rating}/5.0"
        )
        return True

    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return False


def bulk_update():
    google_client = GoogleSheet()
    lab_names = google_client.get_all_lab_names()
    repositories = []
    for name in lab_names:
        repositories.extend(google_client.get_all_repositories(sheet_name=name))

    for owner, repository in repositories:
        run(owner=owner, repository=repository)


if __name__ == "__main__":
    # Get repository from environment variable (when run by GitHub Actions)
    # or use default for local testing
    github_repository = os.getenv("GITHUB_REPOSITORY", "nuwm-lab/30-array-of-objects-Ivanvasylcuk")
    
    logger.info(f"Starting PR Agent for repository: {github_repository}")
    
    # Split owner/repo
    try:
        owner, repository = github_repository.split("/")
    except ValueError:
        logger.error(f"Invalid GITHUB_REPOSITORY format: {github_repository}")
        logger.error("Expected format: owner/repository")
        exit(1)
    
    # To run the process for all repositories, uncomment the line below
    # bulk_update()

    success = run(owner=owner, repository=repository)
    if success:
        logger.info("Process completed successfully.")
    else:
        logger.error("Process failed.")
