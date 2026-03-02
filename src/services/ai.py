from typing import List, Dict
import openai

import config


class AiRequest:
    def __init__(
            self,
            context: List[Dict[str, str]],
            model: str = config.OPENAI_MODEL,
    ):
        self.context = context
        self.model = model

    def get_response(
            self,
    ) -> str:
        """
        Get response from OpenAI
        :return response: OpenAI response
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.context
        )
        return response.choices[0].message
