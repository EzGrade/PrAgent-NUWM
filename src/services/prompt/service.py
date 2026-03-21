"""
Prompt Generator Service
"""

from typing import Dict, List, Optional, Union
from random import choice

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
            teacher_prompts: Optional[List[str]] = None
    ):
        """
        :param system_prompt: Plain text prompt for the system
        :param context_prompt: Dict of files and their content {"file_name": "file_content"}
        """
        self.system_prompt: str = system_prompt
        self.student_assignment: Optional[str] = student_assignment
        self.context_prompt: Optional[Dict[str, str]] = context_prompt
        self.teacher_prompts: Optional[List[str]] = teacher_prompts
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

    def get_system_prompt(self) -> Dict[str, str]:
        """
        :return system_prompt: System prompt
        """
        return {
            "role": "system",
            "content": self.system_prompt,
        }

    def get_student_assignment(self) -> Optional[str]:
        """
        :return student_assignment: Student assignment
        """
        if self.student_assignment:
            return {
                "role": "user",
                "content": f"Student assignment: {self.student_assignment}",
            }
        return None

    def get_teacher_prompt(self) -> Optional[List[str]]:
        """
        :return teacher_prompt: Teacher prompt
        """
        if self.teacher_prompts:
            return {
                "role": "system",
                "content": f"Teacher prompt: {choice(self.teacher_prompts)}",
            }
        return None

    def get_prompt(self) -> List[Dict[str, str]]:
        """
        :return messages: List of messages for chat context
        [{role: "system", content: "system_prompt"}, {role: "user", content: "context_prompt"}]
        """
        logger.debug("Generating prompt messages")
        messages: List[Dict[str, str]] = []

        system_prompt_message: Dict[str, str] = self.get_system_prompt()
        messages.append(system_prompt_message)

        student_assignment_message = self.get_student_assignment()
        if student_assignment_message:
            messages.append(student_assignment_message)

        teacher_prompt_message = self.get_teacher_prompt()
        if teacher_prompt_message:
            messages.append(teacher_prompt_message)

        messages.extend(self.files_to_dict())
        return messages
