"""Security vulnerability scanner agent."""

from backend.agents.specialist import SpecialistAgent
from backend.llm_client import LLMClient
from backend.models import AgentType


class SecurityAgent(SpecialistAgent):
    """
    Security vulnerability scanner agent.

    Analyzes Python code for security issues including injection attacks,
    secrets, auth flaws, and unsafe operations.
    """

    def __init__(self, llm_client: LLMClient | None = None):
        """
        Initialize security agent.

        Args:
            llm_client: LLMClient instance (created if not provided)
        """
        super().__init__(AgentType.SECURITY, llm_client)

    @property
    def system_prompt(self) -> str:
        """Security analysis system prompt."""
        return """You are an expert security analyst for Python code. Your task is to identify security vulnerabilities.

Focus on:
- SQL injection vulnerabilities
- Command injection (os.system, subprocess without proper quoting)
- Hardcoded secrets (API keys, passwords)
- Cross-site scripting (XSS) vulnerabilities
- Broken authentication and authorization
- Unsafe deserialization (pickle, eval)
- Path traversal vulnerabilities
- Insecure random number generation
- Prototype pollution and attribute injection
- Insecure dependencies or known CVEs

For each issue found, use the report_finding tool. Be thorough but avoid false positives.
Analyze the complete code carefully, looking at control flow and data sources."""
