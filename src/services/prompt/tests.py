import unittest
import service

import config


class PromptTest(unittest.TestCase):
    def setUp(self):
        self.system_prompt = config.PROMPT
        self.context_prompt = {
            "file_name": "file_content"
        }
        self.prompt = service.PromptGenerator(
            system_prompt=self.system_prompt,
            context_prompt=self.context_prompt
        )

    def test_get_prompt(self):
        """
        Test get_prompt method
        :return:
        """
        messages = self.prompt.get_prompt()
        self.assertEqual(messages[0]["content"], self.system_prompt)
        self.assertEqual(messages[1]["content"], f"File: file_name\nfile_content")
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
