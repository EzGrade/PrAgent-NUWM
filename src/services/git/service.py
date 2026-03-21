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
    logger.debug("Converting paginator to list")
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
        logger.debug(f"Leaving comment on PR: {comment}")
        if not pull_number:
            pull_number = self.last_pr_number

        pr = self.repository.get_pull(pull_number)
        pr.create_issue_comment(comment)
        logger.info(f"Comment left on PR number: {pull_number}")

    def get_pr_creator(self, pull_number: Optional[int] = None) -> str:
        """
        Get the creator of the pull request
        :param pull_number: The number of the pull request
        :return: The username of the creator of the pull request
        """
        logger.debug("Getting PR creator")
        if not pull_number:
            pull_number = self.last_pr_number

        pr = self.repository.get_pull(pull_number)
        creator = pr.user.login
        logger.info(f"PR creator: {creator}")
        return creator


if __name__ == "__main__":
    github = GitHub(owner="nuwm-lab", repo="Simple-Test")
    github.leave_comment_on_pr("some_comment")
