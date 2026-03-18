"""
AI Service
"""

from typing import List, Dict
import openai

import config


class AiRequest:
    """
    AI Request service
    """

    def __init__(
            self,
            context: List[Dict[str, str]],
            model: str = config.OPENAI_MODEL,
    ):
        """
        Initialize AI Request service
        :param context:
        :param model:
        """
        self.context = context
        self.model = model

        self.client = self.get_client()

    @staticmethod
    def get_client() -> openai.OpenAI:
        """
        Get OpenAI client
        :return:
        """
        return openai.OpenAI(
            api_key=config.OPENAI_API_KEY,
        )

    def get_response(
            self,
    ) -> str:
        """
        Get response from OpenAI
        :return response: OpenAI response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.context
        )
        return response.choices[0].message.content
