from typing import List, Dict, Union, Optional
from github.File import File
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from github import GithubIntegration, Auth
import config
from utils.logger import setup_logger

logger = setup_logger(__name__)
GithubEntity = Union[Repository, File]


def paginator_to_list(
        paginator: PaginatedList[Union[Repository, File]]
) -> List[GithubEntity]:
    """
    Convert paginator to list
    :param paginator: PaginatedList of Repository or File
    :return: List of Repository or File
    """
    return [obj for obj in paginator]


class GitHub:
    """
    This class is used to interact with the GitHub API.
    """

    def __init__(
            self,
            installation_id: Optional[int] = None,
            owner: Optional[str] = None,
            repo: Optional[str] = None
    ):
        logger.info("Initializing GitHub client")
        self.owner = owner
        self.repo = repo

        self.auth = Auth.AppAuth(
            app_id=config.GITHUB_APP_ID,
            private_key=config.GITHUB_PRIVATE_KEY,
        )

        self.app_client = GithubIntegration(auth=self.auth)

        self.installation_id = installation_id or self.get_installation_id()
        self.client = self.app_client.get_github_for_installation(installation_id=self.installation_id)
        self.repository = self.client.get_repo(f"{owner}/{repo}")
        self.last_pr_number = self.get_last_pr_number()
        logger.info("GitHub client initialized")

    def get_installation_id(self) -> int:
        """
        Get installation id for the repository
        :return: installation id
        """
        logger.debug("Getting installation ID")
        installations = self.app_client.get_installations()
        for installation in installations:
            logger.info(f"Installation: {installation}")
            repo = paginator_to_list(installation.get_repos())[0]
            owner = repo.owner.login
            name = repo.name
            logger.info(f"Owner: {owner}, Name: {name}")
            if owner == self.owner:
                logger.debug(f"Found installation ID: {installation.id}")
                return installation.id
        logger.error("Installation not found")
        raise RuntimeError("Installation not found")

    def get_pr_files_content(self) -> Dict[str, str]:
        """
        Get content of the files in the last PR
        :return: Dictionary with file paths as keys and file contents as values
        """
        logger.debug("Getting PR files content")

        def get_files_recursively(path: str, ref: str) -> Dict[str, str]:
            logger.debug(f"Getting files recursively from path: {path}, ref: {ref}")
            files = self.repository.get_contents(path, ref=ref)
            context = dict()
            for file in files:
                if file.type == "dir":
                    context.update(get_files_recursively(file.path, ref))
                else:
                    context[file.path] = file.decoded_content.decode("utf-8")
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

    def leave_comment_on_pr(
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

    def get_student(self, all_nicknames: List[str]) -> str:
        """
        Get the author of the last commit.
        :return: The username or the email of the author of the last commit
        """
        logger.debug("Getting last commit author")
        repository_name = self.repository.full_name
        lab_name = repository_name.split("/")[-1]
        for nickname in all_nicknames:
            if nickname in lab_name:
                logger.info(f"Student nickname: {nickname}")
                return nickname
        return None

    def get_lab_name(self, student_nickname: str) -> str:
        """
        Get the name of the lab.
        :return: The name of the lab
        """
        logger.debug("Getting lab name")
        repository_name = self.repository.full_name
        lab_name = repository_name.split("/")[-1]
        lab_name = lab_name.replace(f"-{student_nickname}", "")
        logger.info(f"Lab name: {lab_name}")
        return lab_name

    def get_last_pr_link(self) -> str:
        """
        Get the link to the last PR.
        :return: The link to the last PR
        """
        logger.debug("Getting last PR link")
        link = f"https://github.com/{self.owner}/{self.repo}/pull/{self.last_pr_number}"
        return link

    def get_lab_number(self, student_nickname) -> int:
        """
        Get the lab number.
        :return: The lab number
        """
        logger.debug("Getting lab number")
        lab_name = self.get_lab_name(student_nickname=student_nickname)
        lab_number = lab_name.split("-")[0]
        lab_number = int(lab_number) // 10
        return lab_number


if __name__ == "__main__":
    github = GitHub(owner="nuwm-lab", repo="Simple-Test")
    github.leave_comment_on_pr("some_comment")
