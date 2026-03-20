"""
AI Service
"""

from typing import List, Dict
import openai

import config
from utils.logger import setup_logger

logger = setup_logger(__name__)


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
        logger.debug("Initializing AiRequest with model: %s", model)
        self.context = context
        self.model = model

        self.client = self.get_client()
        logger.debug("OpenAI client initialized")

    @staticmethod
    def get_client() -> openai.OpenAI:
        """
        Get OpenAI client
        :return:
        """
        logger.debug("Getting OpenAI client")
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
        logger.debug("Getting response from OpenAI with context: %s", self.context)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.context
        )
        logger.debug("Received response from OpenAI")
        return response.choices[0].message.content
