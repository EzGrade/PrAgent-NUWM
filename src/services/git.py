from typing import List, Dict, Union

from github.File import File
from github.PaginatedList import PaginatedList
from github.Repository import Repository

import config
from github import GithubIntegration, Auth


def paginator_to_list(
        paginator: PaginatedList[Repository]
) -> List[Union[Repository, File]]:
    all_pages = []
    for obj in paginator:
        all_pages.append(obj)
    return all_pages


class GitHub:
    def __init__(
            self,
            private_key: str = config.GITHUB_PRIVATE_KEY,
            app_id: int = config.GITHUB_APP_ID,
            installation_id: int = config.GITHUB_INSTALLATION_ID,
            owner: str = None,
            repo: str = None
    ):
        self.owner = owner
        self.repo = repo

        self.auth = Auth.AppAuth(
            app_id=app_id,
            private_key=private_key,
        )

        self.app_client = GithubIntegration(auth=self.auth)

        if not installation_id:
            self.installation_id = self.get_installation_id()
        else:
            self.installation_id = int(installation_id)

        self.client = self.app_client.get_github_for_installation(
            installation_id=self.installation_id,
        )

        self.repository = self.get_repo(f"{owner}/{repo}")

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
        raise Exception("Installation not found")

    def get_repo(
            self,
            repo_name: str
    ) -> Repository:
        return self.client.get_repo(repo_name)

    def get_pr_files_content(
            self,
    ) -> Dict[str, str]:
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
        pr_number = self.repository.get_pulls(sort="decr")
        return pr_number[0].number

    def leave_comment_on_pr(
            self,
            comment: str,
            pull_number: int = None
    ):
        if not pull_number:
            pull_number = self.get_last_pr_number()

        pr = self.repository.get_pull(pull_number)
        return pr.create_issue_comment(comment)


if __name__ == "__main__":
    github = GitHub(owner="nuwm-lab", repo="Simple-Test")
    github.leave_comment_on_pr("some_comment")
