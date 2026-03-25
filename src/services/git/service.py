from typing import List, Dict, Union, Optional

from loguru import logger
from github.File import File
from github.Repository import Repository

from ...clients.github import GithubClient

GithubEntity = Union[Repository, File]


class GitHub:
    """
    This class is used to interact with the GitHub API.
    """

    def __init__(
            self,
            owner: Optional[str] = None,
            repo: Optional[str] = None
    ):
        self.github_client = GithubClient()

        self.__owner = owner
        self.__repo = repo

        self.repository = self.github_client.get_repo(owner, repo)
        self.last_pr_number = self.get_last_pr_number()

    def get_pr_files_content(self) -> Dict[str, str]:
        """
        Get content of the files in the last PR
        :return: Dictionary with file paths as keys and file contents as values
        """

        def get_files_recursively(path: str, ref: str) -> Dict[str, str]:
            logger.debug(f"Getting files recursively from path: {path}, ref: {ref}")
            files = self.repository.get_contents(path, ref=ref)
            context = dict()
            encodings = ['utf-8', 'latin-1', 'cp1252']
            for file in files:
                if file.type == "dir":
                    context.update(get_files_recursively(file.path, ref))
                else:
                    for encoding in encodings:
                        try:
                            content = file.decoded_content.decode(encoding)
                            context[file.path] = content
                            break
                        except UnicodeDecodeError:
                            continue
            return context

        last_pr = self.repository.get_pull(self.last_pr_number)
        logger.info(f"Last PR number: {self.last_pr_number}")
        return get_files_recursively("", last_pr.head.ref)

    def get_last_pr_number(self) -> int:
        """
        Get last PR number
        :return:
        """
        logger.debug("Getting last PR number")
        pr_number = self.repository.get_pulls(sort="created", direction="desc")
        logger.info(f"Last PR number: {pr_number[0].number}")
        return pr_number[0].number

    def comment_pr(
            self,
            comment: str,
            pull_number: Optional[int] = None
    ) -> None:
        """
        Leave comment on last PR
        :param comment: Comment to leave
        :param pull_number: PR number to comment on
        """
        if not pull_number:
            pull_number = self.last_pr_number

        pr = self.repository.get_pull(pull_number)
        pr.create_issue_comment(comment)
        logger.info(f"Comment left on PR number: {pull_number}")

    def get_student(self, lab_name: str) -> str:
        """
        Get the author of the last commit.
        :return: The username or the email of the author of the last commit
        """
        logger.debug("Getting last commit author")
        repository_name = self.repository.full_name
        _lab_name = repository_name.split("/")[-1]
        student = _lab_name.replace(f"{lab_name}-", "")
        return student

    def get_lab_name(self, all_lab_names: List[str]) -> str:
        """
        Get the name of the lab.
        :return: The name of the lab
        """
        logger.debug("Getting lab name")
        repository_name = self.repository.full_name
        lab_name = repository_name.split("/")[-1]
        for _lab_name in all_lab_names:
            if _lab_name in lab_name:
                lab_name = _lab_name
                break
        logger.info(f"Lab name: {lab_name}")
        return lab_name

    def get_last_pr_link(self) -> str:
        """
        Get the link to the last PR.
        :return: The link to the last PR
        """
        logger.debug("Getting last PR link")
        link = f"https://github.com/{self.__owner}/{self.__repo}/pull/{self.last_pr_number}"
        return link
