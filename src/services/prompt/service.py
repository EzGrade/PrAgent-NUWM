"""
Prompt Generator Service
"""

from typing import Dict, List, Optional, Union

from config import PROMPT
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PromptGenerator:
    """
    Class to generate prompt for the system and contextД
    """

    def __init__(
            self,
            system_prompt: str = PROMPT,
            student_assignment: Optional[str] = None,
            context_prompt: Optional[Dict[str, str]] = None,
    ):
        """
        :param system_prompt: Plain text prompt for the system
        :param context_prompt: Dict of files and their content {"file_name": "file_content"}
        """
        logger.debug("Initializing PromptGenerator with system_prompt: %s, student_assignment: %s", system_prompt,
                     student_assignment)
        self.system_prompt: str = system_prompt
        self.student_assignment: Optional[str] = student_assignment
        self.context_prompt: Optional[Dict[str, str]] = context_prompt
        self.context: Optional[List[Dict[str, Union[str, str]]]] = None

    def files_to_dict(self) -> List[Dict[str, str]]:
        """
        Convert files to dict for chat context
        :return: List of messages for chat context
        """
        logger.debug("Converting files to dict")
        messages = []
        if self.context_prompt:
            for file_name, file_content in self.context_prompt.items():
                logger.debug("Processing file: %s", file_name)
                content = f"File: {file_name}\n{file_content}"
                context_prompt_message = {
                    "role": "user",
                    "content": content,
                }
                messages.append(context_prompt_message)
        return messages

    def get_prompt(self) -> List[Dict[str, str]]:
        """
        :return messages: List of messages for chat context
        [{role: "system", content: "system_prompt"}, {role: "user", content: "context_prompt"}]
        """
        logger.debug("Generating prompt messages")
        messages: List[Dict[str, str]] = []

        system_prompt_message: Dict[str, str] = {
            "role": "system",
            "content": self.system_prompt,
        }
        messages.append(system_prompt_message)
        logger.debug("Added system prompt message")

        if self.student_assignment:
            student_assignment_message: Dict[str, str] = {
                "role": "user",
                "content": f"Assignment: {self.student_assignment}",
            }
            messages.append(student_assignment_message)
            logger.debug("Added student assignment message")

        messages.extend(self.files_to_dict())
        logger.debug("Added context prompt messages")
        return messages
