from github import GithubIntegration, Auth
from github.Repository import Repository

from configs.github import GitHubConfig
from utils.helpers.paginator import to_list


class GithubClient:
    def __init__(self):
        self.__config = GitHubConfig()  # type: ignore
        self.__owner, self.__repo = self.__config.REPOSITORY.split("/")

        self.__auth = Auth.AppAuth(
            app_id=self.__config.APP_ID,
            private_key=self.__config.PRIVATE_KEY,
        )
        self.__app_client = GithubIntegration(auth=self.__auth)

        self.__installation_id = self.get_installation_id()
        self.__client = self.__app_client.get_github_for_installation(
            installation_id=self.__installation_id
        )

    def get_installation_id(self) -> int:
        installations = self.__app_client.get_installations()
        for installation in installations:
            repo = to_list(installation.get_repos())

            if not repo:
                continue

            repo = repo[0]
            owner = repo.owner.login
            if owner == self.__owner:
                return installation.id

        raise RuntimeError("Installation not found")

    def get_repo(self, owner: str, repo_name: str) -> Repository:
        text = f"{owner}/{repo_name}"
        return self.__client.get_repo(text)
