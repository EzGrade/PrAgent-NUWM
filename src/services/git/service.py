"""
This module contains the GitHub class that is used to interact with the GitHub API.
"""

from typing import List, Dict, Union

from github.File import File
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from github import GithubIntegration, Auth

import config


def paginator_to_list(
        paginator: PaginatedList[Repository]
) -> List[Union[Repository, File]]:
    """
    Convert paginator to list
    :param paginator:
    :return:
    """
    all_pages = []
    for obj in paginator:
        all_pages.append(obj)
    return all_pages


class GitHub:
    """
    This class is used to interact with the GitHub API.
    """

    def __init__(
            self,
            installation_id: int = config.GITHUB_INSTALLATION_ID,
            owner: str = None,
            repo: str = None
    ):
        self.owner = owner
        self.repo = repo

        self.auth = Auth.AppAuth(
            app_id=config.GITHUB_APP_ID,
            private_key=config.GITHUB_PRIVATE_KEY,
        )

        self.app_client = GithubIntegration(auth=self.auth)

        if not installation_id:
            self.installation_id = self.get_installation_id()
        else:
            self.installation_id = int(installation_id)

        self.client = self.app_client.get_github_for_installation(
            installation_id=self.installation_id,
        )

        self.repository = self.client.get_repo(f"{owner}/{repo}")

    def get_installation_id(
            self,
    ) -> str:
        """
        Get installation id for the repository
        :return id: installation id
        """
        installations = self.app_client.get_installations()
        for installation in installations:
            repos = paginator_to_list(installation.get_repos())
            for repo in repos:
                owner = repo.owner.login
                name = repo.name
                if owner == self.owner and name == self.repo:
                    return installation.id
        raise RuntimeError("Installation not found")

    def get_pr_files_content(
            self,
    ) -> Dict[str, str]:
        """
        Get content of the files in the last PR
        :return:
        """

        def get_files_recursively(path: str, ref: str) -> Dict[str, str]:
            files = self.repository.get_contents(path, ref=ref)
            context = {}
            for file in files:
                if file.type == "dir":
                    context.update(get_files_recursively(file.path, ref))
                else:
                    context[file.path] = file.decoded_content.decode("utf-8")
            return context

        last_pr = self.repository.get_pull(self.get_last_pr_number())
        return get_files_recursively("", last_pr.head.ref)

    def get_last_pr_number(
            self
    ) -> int:
        """
        Get last PR number
        :return:
        """
        pr_number = self.repository.get_pulls(sort="decr")
        return pr_number[0].number

    def leave_comment_on_pr(
            self,
            comment: str,
            pull_number: int = None
    ):
        """
        Leave comment on last PR
        :param comment:
        :param pull_number:
        :return:
        """
        if not pull_number:
            pull_number = self.get_last_pr_number()

        pr = self.repository.get_pull(pull_number)
        return pr.create_issue_comment(comment)


if __name__ == "__main__":
    github = GitHub(owner="nuwm-lab", repo="Simple-Test")
    github.leave_comment_on_pr("some_comment")
