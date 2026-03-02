from typing import Dict, List, Optional


class PromptGenerator:
    def __init__(
            self,
            system_prompt: str,
            context_prompt: Dict[str, str],
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
            "message": self.system_prompt,
        }
        messages.append(system_prompt_message)

        for file_name, file_content in self.context_prompt.items():
            context_prompt_message: Dict[str, str] = {
                "role": "user",
                "message": file_content,
            }
            messages.append(context_prompt_message)

        return messages
