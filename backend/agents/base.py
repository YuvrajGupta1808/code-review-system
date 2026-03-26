"""Base agent interface with LangGraph support."""

from abc import ABC, abstractmethod
from typing import Any, Callable

from backend.models import AgentResult, AgentType, BaseEvent


class BaseAgent(ABC):
    """
    Abstract base class for all review agents.

    Agents can be implemented with:
    - **LangGraph StateGraph** (for coordinator and complex workflows)
    - **Direct LLM streaming** (for specialist agents)

    All agents share the same interface: async analyze() that emits events.
    """

    def __init__(self, agent_id: AgentType):
        """
        Initialize the agent.

        Args:
            agent_id: The agent's identifier (must be an AgentType enum value)
        """
        self.agent_id = agent_id

    @abstractmethod
    async def analyze(
        self,
        code: str,
        context: dict[str, Any],
        event_callback: Callable[[BaseEvent], Any],
    ) -> AgentResult:
        """
        Analyze code and emit events during processing.

        Implementations should:
        1. Emit agent_started event
        2. Perform analysis (emitting thinking, tool_calls, findings as appropriate)
        3. Emit agent_completed on success or agent_error on failure
        4. Return AgentResult with findings

        Args:
            code: The Python code to analyze
            context: Shared context including:
                - metadata (e.g., filename, code_id)
                - previous_findings from other agents (for conflict resolution)
                - any other context needed for analysis
            event_callback: Async callable to emit events: await event_callback(event)

        Returns:
            AgentResult with findings list, errors, and metadata

        Raises:
            Any exceptions should be caught and emitted as agent_error events.
        """
        raise NotImplementedError
