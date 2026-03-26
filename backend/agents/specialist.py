"""Shared specialist agent base class for LLM-based analysis."""

import json
import traceback
from abc import abstractmethod
from typing import Any, Callable
from uuid import uuid4

from backend.agents.base import BaseAgent
from backend.llm_client import (
    LLMClient,
    TextChunk,
    ThinkingChunk,
    ToolCallChunk,
    ToolCallResultChunk,
)
from backend.models import (
    AgentCompletedEvent,
    AgentErrorEvent,
    AgentResult,
    AgentStartedEvent,
    AgentType,
    BaseEvent,
    Finding,
    FindingDiscoveredEvent,
    FixProposedEvent,
    Severity,
    ToolCallResultEvent,
    ToolCallStartEvent,
    ThinkingEvent,
)

# Tool definition for specialists (same for all)
REPORT_FINDING_TOOL = {
    "type": "function",
    "function": {
        "name": "report_finding",
        "description": "Report a finding in the code",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Category of the issue (e.g., sql_injection, null_reference)",
                },
                "severity": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low", "info"],
                    "description": "Severity level of the finding",
                },
                "line_number": {
                    "type": "integer",
                    "description": "Line number where the issue is found",
                },
                "description": {
                    "type": "string",
                    "description": "Description of the issue",
                },
                "code_snippet": {
                    "type": "string",
                    "description": "Relevant code snippet from the code being analyzed",
                },
                "fix_suggestion": {
                    "type": "string",
                    "description": "Suggested fix for the issue (optional)",
                },
            },
            "required": [
                "category",
                "severity",
                "line_number",
                "description",
                "code_snippet",
            ],
        },
    },
}


class SpecialistAgent(BaseAgent):
    """
    Base class for specialist agents (Security, Bug Detection, etc.).

    Handles shared LLM streaming logic and event emission.
    Subclasses only need to define the system prompt.
    """

    def __init__(self, agent_id: AgentType, llm_client: LLMClient | None = None):
        """
        Initialize the specialist agent.

        Args:
            agent_id: Agent identifier (SECURITY, BUG_DETECTION, etc.)
            llm_client: LLMClient instance (created if not provided)
        """
        super().__init__(agent_id)
        self.llm_client = llm_client or LLMClient()

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this specialist."""
        raise NotImplementedError

    async def analyze(
        self,
        code: str,
        context: dict[str, Any],
        event_callback: Callable[[BaseEvent], Any],
    ) -> AgentResult:
        """
        Analyze code using LLM streaming with shared event emission.

        Emits: started → thinking* → tool_call_* → finding_discovered* → completed or error

        Args:
            code: Python code to analyze
            context: Analysis context (metadata, previous findings, etc.)
            event_callback: Async callable for emitting events

        Returns:
            AgentResult with findings
        """
        findings: list[Finding] = []
        errors: list[str] = []

        try:
            # Emit agent started
            await event_callback(AgentStartedEvent(agent_id=self.agent_id, data={}))

            # Build messages
            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"Analyze this Python code:\n\n{code}",
                },
            ]

            # Stream from LLM
            async for chunk in self.llm_client.stream_completion(
                messages, tools=[REPORT_FINDING_TOOL]
            ):
                if isinstance(chunk, ThinkingChunk) and chunk.delta:
                    await event_callback(
                        ThinkingEvent(agent_id=self.agent_id, data={"content": chunk.delta})
                    )

                elif isinstance(chunk, TextChunk) and chunk.delta:
                    # Text responses between tool calls
                    pass

                elif isinstance(chunk, ToolCallChunk):
                    await event_callback(
                        ToolCallStartEvent(
                            agent_id=self.agent_id,
                            data={"tool_name": chunk.tool_name, "input": {}},
                        )
                    )

                elif isinstance(chunk, ToolCallResultChunk):
                    if chunk.tool_name == "report_finding":
                        try:
                            args = json.loads(chunk.args_json)

                            # Emit tool call result
                            await event_callback(
                                ToolCallResultEvent(
                                    agent_id=self.agent_id,
                                    data={
                                        "tool_name": "report_finding",
                                        "output": json.dumps(args),
                                        "duration_ms": 0,
                                    },
                                )
                            )

                            # Create finding
                            finding = Finding(
                                finding_id=str(uuid4()),
                                category=args.get("category", "unknown"),
                                severity=Severity(args.get("severity", "medium")),
                                line=args.get("line_number", 0),
                                description=args.get("description", ""),
                                agent_id=self.agent_id,
                            )
                            findings.append(finding)

                            # Emit finding discovered
                            await event_callback(
                                FindingDiscoveredEvent(
                                    agent_id=self.agent_id,
                                    data={
                                        "finding_id": finding.finding_id,
                                        "category": finding.category,
                                        "severity": finding.severity.value,
                                        "line": finding.line,
                                        "description": finding.description,
                                    },
                                )
                            )

                            # Optionally emit fix if provided
                            if args.get("fix_suggestion"):
                                await event_callback(
                                    FixProposedEvent(
                                        agent_id=self.agent_id,
                                        data={
                                            "finding_id": finding.finding_id,
                                            "original_code": args.get("code_snippet", ""),
                                            "proposed_fix": args.get("fix_suggestion", ""),
                                            "explanation": args.get("description", ""),
                                            "confidence": 0.8,
                                        },
                                    )
                                )
                        except json.JSONDecodeError as e:
                            errors.append(f"Failed to parse tool args: {e}")

            # Emit completion
            await event_callback(AgentCompletedEvent(agent_id=self.agent_id, data={}))

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            errors.append(error_msg)
            await event_callback(
                AgentErrorEvent(
                    agent_id=self.agent_id,
                    data={"error": error_msg, "traceback": traceback.format_exc()},
                )
            )
            raise

        return AgentResult(agent_id=self.agent_id, findings=findings, errors=errors, metadata={})
