from loguru import logger

from src.clients.openai import OpenAIClient
from src.models.llm.tools import ReviewCodeTool


class AiRequest:
    def __init__(self):
        self.client = OpenAIClient()

    def send_message(self, context: list[dict[str, str]]) -> ReviewCodeTool:
        response = self.client.send_message(context, tools=[ReviewCodeTool])
        tool_call = response.tool_calls[0].tool_input

        try:
            return ReviewCodeTool.model_validate(tool_call)
        except Exception as e:
            logger.error(f"Error parsing review: {e}")
            raise
