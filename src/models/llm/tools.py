from typing import Any

import jsonref
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    tool_name: str = Field()
    tool_input: dict = Field()
    tool_id: str = Field()

    def to_dict(self) -> dict:
        return {
            "type": "tool_use",
            "id": self.tool_id,
            "name": self.tool_name,
            "input": self.tool_input,
        }


class LLMResponse(BaseModel):
    text: str = Field()
    tool_calls: list[ToolCall] = Field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)

    @property
    def has_tool_result(self) -> bool:
        return self.tool_result is not None


class BaseTool(BaseModel):

    @classmethod
    def prepare_schema(cls, *args, **kwargs) -> dict[str, Any]:
        """
        Prepare the JSON schema for the parties tool.
        This method is used to prepare the JSON schema for the parties tool.
        """
        schema = jsonref.replace_refs(
            cls.model_json_schema(), lazy_load=False, proxies=False
        )
        schema.pop("$defs", None)
        return schema

    @classmethod
    def to_openai_tool_definition(cls, **kwargs) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": cls.__name__,
                "description": cls.__doc__,
                "parameters": cls.prepare_schema(**kwargs),
            },
        }


class ReviewCodeTool(BaseTool):
    comment: str = Field(..., description="Comment to student code")
    suggestions: str = Field(..., description="Suggestions for improving the code")
    rating: float = Field(..., description="Rating for the comment. On a scale from 1 to 5")

    @property
    def message(self) -> str:
        return f"# Коментар\n{self.comment}\n\n# Пропозиції\n{self.suggestions}\n\n# Оцінка: {self.rating}"
