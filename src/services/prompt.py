"""
Prompt Generator Service
"""

from typing import Dict, List, Optional

from config import PROMPT


class PromptGenerator:
    """
    Class to generate prompt for the system and context
    """

    def __init__(
            self,
            system_prompt: str = PROMPT,
            context_prompt: Dict[str, str] = None,
    ):
        """
        :param system_prompt: Plain text prompt for the system
        :param context_prompt: Dict of files and their content {"file_name": "file_content"}
        """
        self.system_prompt: str = system_prompt
        self.context_prompt: Dict[str, str] = context_prompt
        self.context: Optional[None, List[Dict[str, str]]] = None

    def files_to_dict(self):
        """
        Convert files to dict for chat context
        :return:
        """
        messages = []
        for file_name, file_content in self.context_prompt.items():
            content = f"File: {file_name}\n{file_content}"
            context_prompt_message = {
                "role": "user",
                "content": content,
            }
            messages.append(context_prompt_message)
        return messages

    def get_prompt(
            self
    ) -> List[Dict[str, str]]:
        """
        :return messages: List of messages for chat context
        [{role: "system", message: "system_prompt"}, {role: "user", message: "context_prompt"}]
        """
        messages: List[Dict[str, str]] = []

        system_prompt_message: Dict[str, str] = {
            "role": "system",
            "content": self.system_prompt,
        }
        messages.append(system_prompt_message)
        messages.extend(self.files_to_dict())
        return messages
