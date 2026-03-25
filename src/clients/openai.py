from json import loads, JSONDecodeError

from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletion

from ..configs.openai import OpenAIConfig
from ..models.llm.tools import BaseTool, LLMResponse, ToolCall


class OpenAIClient:
    def __init__(self):
        self.__config = OpenAIConfig()  # type: ignore

        self.__client = OpenAI(
            api_key=self.__config.API_KEY
        )

    def send_message(self, messages: list, tools: list[type[BaseTool]] | None = None) -> LLMResponse:
        prepared_tools = [tool.to_openai_tool_definition() for tool in tools]
        response = self.__client.chat.completions.create(
            model=self.__config.MODEL,
            messages=messages,
            tools=prepared_tools
        )

        return self.__parse_response(response)

    @staticmethod
    def __parse_response(response: ChatCompletion) -> LLMResponse:
        if not response.choices:
            raise ValueError("No choices in OpenAI API response")

        choice = response.choices[0]
        tool_calls = []

        if not choice.message.tool_calls:
            raise ValueError("No tool calls in OpenAI API response")

        for call in choice.message.tool_calls:
            try:
                if isinstance(call.function.arguments, str):
                    arguments = loads(call.function.arguments)
                else:
                    arguments = call.function.arguments
            except JSONDecodeError as e:
                logger.warning(f"Error decoding JSON in tool call arguments: {e}")
                logger.debug(f"Raw arguments: {call.function.arguments}")
                raise RuntimeError("Couldn't decode tool call arguments") from e

            tool_calls.append(
                ToolCall(
                    tool_name=call.function.name,
                    tool_input=arguments,
                    tool_id=call.id,
                )
            )

        return LLMResponse(
            text=choice.message.content or "",
            tool_calls=tool_calls,
        )
