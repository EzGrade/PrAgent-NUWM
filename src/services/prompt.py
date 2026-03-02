from typing import Dict, List, Optional

from config import PROMPT


class PromptGenerator:
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

        for file_name, file_content in self.context_prompt.items():
            content = f"File: {file_name}\n{file_content}"
            context_prompt_message: Dict[str, str] = {
                "role": "user",
                "content": content,
            }
            messages.append(context_prompt_message)

        return messages
