"""
Git service tests
"""

import unittest
from service import GitHub
import config


class GitTests(unittest.TestCase):
    """
    Git service tests
    """

    def test_init(self):
        """
        Test GitHub class initialization
        :return:
        """
        github = GitHub(
            owner=config.GITHUB_REPOSITORY_OWNER,
            repo=config.GITHUB_REPOSITORY_NAME
        )
        self.assertEqual(github.owner, config.GITHUB_REPOSITORY_OWNER)
        self.assertEqual(github.repo, config.GITHUB_REPOSITORY_NAME)

    def setUp(self):
        """
        Setup GitHub class
        :return:
        """
        self.owner = config.GITHUB_REPOSITORY_OWNER
        self.repo = config.GITHUB_REPOSITORY_NAME
        self.github = GitHub(
            owner=self.owner,
            repo=self.repo
        )
