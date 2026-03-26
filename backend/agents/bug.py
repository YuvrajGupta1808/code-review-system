"""Bug detection agent for code analysis."""

from backend.agents.specialist import SpecialistAgent
from backend.llm_client import LLMClient
from backend.models import AgentType


class BugAgent(SpecialistAgent):
    """
    Bug detection agent for code analysis.

    Analyzes Python code for logical errors, null dereferences,
    type mismatches, resource leaks, and other runtime issues.
    """

    def __init__(self, llm_client: LLMClient | None = None):
        """
        Initialize bug detection agent.

        Args:
            llm_client: LLMClient instance (created if not provided)
        """
        super().__init__(AgentType.BUG_DETECTION, llm_client)

    @property
    def system_prompt(self) -> str:
        """Bug detection system prompt."""
        return """You are an expert code reviewer focused on finding bugs and logical errors in Python code.

Focus on:
- Null/None dereferences and missing null checks
- Unhandled exceptions and missing error handling
- Off-by-one errors in loops and array indexing
- Logic errors and incorrect algorithms
- Type mismatches and incompatible operations
- Uninitialized variables used before assignment
- Race conditions in concurrent code
- Resource leaks (unclosed files, connections, database handles)
- Missing error propagation and silent failures
- Infinite loops or unreachable code
- Incorrect variable scope or shadowing

For each bug found, use the report_finding tool. Focus on actual logic errors and patterns that will cause runtime failures.
Analyze the complete code flow carefully to identify issues."""
