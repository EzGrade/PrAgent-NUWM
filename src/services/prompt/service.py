from random import choice

from loguru import logger


class PromptGenerator:
    def __init__(
            self,
            student_assignment: str | None = None,
            context_prompt: dict[str, str] | None = None,
            teacher_prompts: list[str] | None = None
    ):
        self.student_assignment: str | None = student_assignment
        self.context_prompt: dict[str, str] | None = context_prompt
        self.teacher_prompts: list[str] | None = teacher_prompts
        self.context: str | None = None

    def files_to_dict(self) -> list[dict[str, str]]:
        logger.debug("Converting files to dict")
        messages = []
        if self.context_prompt:
            for file_name, file_content in self.context_prompt.items():
                logger.debug(f"Processing file: {file_name}")
                content = f"File: {file_name}\n{file_content}"
                context_prompt_message = {
                    "role": "user",
                    "content": content,
                }
                messages.append(context_prompt_message)
        return messages

    def get_student_assignment(self) -> dict[str, str] | None:
        if self.student_assignment:
            return {
                "role": "user",
                "content": f"Student assignment: {self.student_assignment}",
            }
        return None

    def get_teacher_prompt(self) -> dict[str, str] | None:
        if self.teacher_prompts:
            return {
                "role": "system",
                "content": f"Teacher prompt: {choice(self.teacher_prompts)}",
            }
        return None

    def get_prompt(self) -> list[dict[str, str]]:
        logger.debug("Generating prompt messages")
        messages: list[dict[str, str]] = []

        teacher_prompt_message = self.get_teacher_prompt()
        if teacher_prompt_message:
            messages.append(teacher_prompt_message)
            self.context = teacher_prompt_message["content"]

        student_assignment_message = self.get_student_assignment()
        if student_assignment_message:
            messages.append(student_assignment_message)
            self.context += f"\n{student_assignment_message['content']}"

        messages.extend(self.files_to_dict())
        return messages
