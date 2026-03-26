"""MiniMax LLM client with streaming support."""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator

from openai import AsyncOpenAI


class ChunkType(str, Enum):
    """Types of chunks yielded by stream."""

    THINKING = "thinking"
    TEXT = "text"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_RESULT = "tool_call_result"


@dataclass
class ThinkingChunk:
    """Chunk containing reasoning/thinking content."""

    type: ChunkType = ChunkType.THINKING
    delta: str = ""


@dataclass
class TextChunk:
    """Chunk containing completion text."""

    type: ChunkType = ChunkType.TEXT
    delta: str = ""


@dataclass
class ToolCallChunk:
    """Chunk starting or continuing a tool call."""

    type: ChunkType = ChunkType.TOOL_CALL_START
    tool_name: str = ""
    tool_call_id: str = ""
    args_delta: str = ""


@dataclass
class ToolCallResultChunk:
    """Chunk containing completed tool call with full arguments."""

    type: ChunkType = ChunkType.TOOL_CALL_RESULT
    tool_name: str = ""
    tool_call_id: str = ""
    args_json: str = ""


class LLMClient:
    """
    OpenAI-compatible client for MiniMax LLM.

    Uses OpenAI Python SDK with MiniMax base URL. Supports streaming with
    reasoning_split to separate thinking/reasoning from generated text.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str = "MiniMax-M2.7",
    ):
        """
        Initialize LLM client.

        Args:
            base_url: OpenAI base URL (default: env OPENAI_BASE_URL or from config)
            api_key: API key (default: env OPENAI_API_KEY, MINIMAX_API_KEY, or from config)
            model: Model name (default: MiniMax-M2.7)
        """
        self.model = model

        # Try multiple sources for credentials
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("MINIMAX_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        # If not in env, try loading from config
        if not self.api_key or not self.base_url:
            try:
                from backend.config import load_settings

                settings = load_settings()
                self.api_key = self.api_key or settings.openai_api_key
                self.base_url = self.base_url or settings.openai_base_url
            except Exception:
                pass

        if not self.base_url or not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY (or MINIMAX_API_KEY) and OPENAI_BASE_URL must be set via env or constructor"
            )

        self.client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

    async def stream_completion(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> AsyncGenerator[ThinkingChunk | TextChunk | ToolCallChunk | ToolCallResultChunk, None]:
        """
        Stream completion from MiniMax with reasoning support.

        Yields typed chunks for thinking, text, and tool calls.
        Reasoning is enabled via extra_body={"reasoning_split": True}.

        Args:
            messages: Chat messages in OpenAI format
            tools: Optional tool definitions (function schema)
            temperature: Sampling temperature (default 0.3 for focused analysis)

        Yields:
            Chunks: ThinkingChunk, TextChunk, ToolCallChunk, ToolCallResultChunk
        """
        # Always enable reasoning_split for interleaved thinking
        extra_body = {"reasoning_split": True}

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            stream=True,
            extra_body=extra_body,
        )

        current_tool_call_id = None
        current_tool_name = None
        current_tool_args = ""

        async for chunk in response:
            if not chunk.choices:
                continue

            choice = chunk.choices[0]

            # Handle reasoning_details (thinking)
            if hasattr(choice, "reasoning_details") and choice.reasoning_details:
                if hasattr(choice.reasoning_details, "thinking"):
                    thinking_text = choice.reasoning_details.thinking
                    if thinking_text:
                        yield ThinkingChunk(delta=thinking_text)

            # Handle delta content
            if choice.delta:
                delta = choice.delta

                # Regular text content
                if delta.content:
                    yield TextChunk(delta=delta.content)

                # Tool calls
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        if tool_call.id:
                            # New tool call starting
                            if current_tool_call_id and current_tool_name:
                                # Emit previous tool call completion
                                yield ToolCallResultChunk(
                                    tool_name=current_tool_name,
                                    tool_call_id=current_tool_call_id,
                                    args_json=current_tool_args,
                                )
                            current_tool_call_id = tool_call.id
                            current_tool_name = tool_call.function.name or ""
                            current_tool_args = ""

                        if tool_call.function and tool_call.function.arguments:
                            current_tool_args += tool_call.function.arguments
                            yield ToolCallChunk(
                                tool_name=current_tool_name or "",
                                tool_call_id=current_tool_call_id or "",
                                args_delta=tool_call.function.arguments,
                            )

            # End of stream - emit final tool call if present
            if choice.finish_reason == "tool_calls":
                if current_tool_call_id and current_tool_name:
                    yield ToolCallResultChunk(
                        tool_name=current_tool_name,
                        tool_call_id=current_tool_call_id,
                        args_json=current_tool_args,
                    )

    async def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """
        Non-streaming completion call.

        Args:
            messages: Chat messages in OpenAI format
            tools: Optional tool definitions (function schema)
            temperature: Sampling temperature

        Returns:
            Response dict with choices, finish_reason, etc.
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            stream=False,
        )
        return response.model_dump()
