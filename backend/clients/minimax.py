"""MiniMax LLM client using OpenAI-compatible API."""

import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

if TYPE_CHECKING:
    from backend.config import Settings

logger = logging.getLogger(__name__)


class TokenKind(str, Enum):
    """Type of token delta from streaming completions."""

    THINKING = "thinking"
    CONTENT = "content"


@dataclass
class TokenDelta:
    """A single streaming token delta."""

    kind: TokenKind
    text: str


@dataclass
class MiniMaxClient:
    """Async LLM client for MiniMax via OpenAI-compatible API.

    Supports streaming completions with reasoning/thinking output.
    Caller is responsible for managing message history across turns.
    """

    base_url: str
    api_key: str
    model: str = "MiniMax-M2.7"
    _client: AsyncOpenAI = field(init=False)

    def __post_init__(self) -> None:
        """Initialize the AsyncOpenAI client."""
        self._client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

    async def stream(
        self,
        messages: list[ChatCompletionMessageParam],
        *,
        system: str | None = None,
    ) -> AsyncGenerator[TokenDelta, None]:
        """Stream thinking and content deltas from MiniMax.

        Args:
            messages: Full conversation history. Caller must maintain and
                     append complete assistant messages (including reasoning_details)
                     for multi-turn interactions.
            system: Optional system prompt (not used in this version;
                   left for future expansion).

        Yields:
            TokenDelta with kind=THINKING for reasoning deltas,
            kind=CONTENT for response content deltas.
        """
        try:
            async with await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                extra_body={"reasoning_split": True},
            ) as stream:
                async for chunk in stream:
                    # Extract delta from the choice
                    delta = chunk.choices[0].delta

                    # Handle reasoning_details (vendor extension)
                    # reasoning_details is a list of objects when reasoning_split=True
                    reasoning_details = getattr(delta, "reasoning_details", None)
                    if reasoning_details is not None and isinstance(reasoning_details, list):
                        for rd in reasoning_details:
                            if isinstance(rd, dict) and rd.get("type") == "thinking":
                                # Extract thinking delta text
                                thinking_delta = rd.get("delta", {})
                                if isinstance(thinking_delta, dict):
                                    thinking_text = thinking_delta.get("thinking", "")
                                    if thinking_text:
                                        yield TokenDelta(
                                            kind=TokenKind.THINKING, text=thinking_text
                                        )

                    # Handle content deltas
                    if delta.content:
                        yield TokenDelta(kind=TokenKind.CONTENT, text=delta.content)

        except Exception as e:
            logger.exception(f"Error during streaming: {e}")
            raise

    async def complete(
        self,
        messages: list[ChatCompletionMessageParam],
        *,
        system: str | None = None,
    ) -> tuple[str, list[ChatCompletionMessageParam]]:
        """Non-streaming completion (convenience method).

        Returns the full content and updated messages list with the
        complete assistant message appended (for multi-turn).

        Args:
            messages: Conversation history.
            system: Optional system prompt (not used in this version).

        Returns:
            Tuple of (content, updated_messages) where updated_messages
            has the full assistant message appended.
        """
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
            extra_body={"reasoning_split": True},
        )

        # Extract content from response
        choice = response.choices[0]
        content = choice.message.content or ""

        # Build updated messages with full assistant message
        # Include reasoning_details if present
        assistant_message: ChatCompletionMessageParam = {
            "role": "assistant",
            "content": content,
        }

        # If the message has reasoning_details, preserve it
        if hasattr(choice.message, "reasoning_details"):
            assistant_message["reasoning_details"] = choice.message.reasoning_details  # type: ignore[typeddict-unknown-key]

        updated_messages = messages + [assistant_message]
        return content, updated_messages


def create_client_from_settings(settings: "Settings") -> MiniMaxClient:
    """Create a MiniMaxClient from application settings.

    Args:
        settings: Application settings with LLM configuration.

    Returns:
        Configured MiniMaxClient instance.
    """
    return MiniMaxClient(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
    )
