import config
import github


class GitHub:
    def __init__(
            self,
            token: str = config.GITHUB_TOKEN,
    ):
        self.token = token
        self.client = github.Github(self.token)

    def get_repo(
            self,
            repo_name: str,
    ):
        """
        Get repository
        :param repo_name: Repository name
        :return repo: Repository object
        """
        repo = self.client.get_repo(repo_name)
        return repo
