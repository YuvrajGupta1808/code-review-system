"""Pydantic models for event streaming and domain objects."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class EventType(str, Enum):
    """All possible event types in the system."""

    # Agent lifecycle
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"

    # Reasoning and tools
    THINKING = "thinking"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_RESULT = "tool_call_result"

    # Findings
    FINDING_DISCOVERED = "finding_discovered"
    FINDINGS_CONSOLIDATED = "findings_consolidated"

    # Coordinator workflow
    PLAN_CREATED = "plan_created"
    AGENT_DELEGATED = "agent_delegated"

    # Final results
    FINAL_REPORT = "final_report"

    # Fixes
    FIX_PROPOSED = "fix_proposed"
    FIX_VERIFIED = "fix_verified"


class AgentType(str, Enum):
    """Agent identifiers."""

    COORDINATOR = "coordinator"
    SECURITY = "security_agent"
    BUG_DETECTION = "bug_agent"


class Severity(str, Enum):
    """Finding severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BaseEvent(BaseModel):
    """Base event structure shared by all events."""

    model_config = ConfigDict(use_enum_values=False)

    event_type: EventType
    agent_id: AgentType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    event_id: str = Field(default_factory=lambda: str(uuid4()))

    @field_serializer("timestamp")
    def _serialize_timestamp(self, v: datetime) -> str:
        """Serialize timestamp to ISO 8601 UTC with Z suffix as per spec."""
        return v.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"

    def to_dict(self) -> dict[str, Any]:
        """Serialize event to JSON-compatible dict for transport.

        Uses Pydantic v2 JSON mode so enums become string values
        and datetime uses the custom field_serializer above.
        """
        return self.model_dump(mode="json")


class AgentStartedEvent(BaseEvent):
    """Emitted when an agent begins analysis."""

    event_type: EventType = EventType.AGENT_STARTED
    data: dict[str, Any] = Field(default_factory=dict)


class AgentCompletedEvent(BaseEvent):
    """Emitted when an agent finishes analysis."""

    event_type: EventType = EventType.AGENT_COMPLETED
    data: dict[str, Any] = Field(default_factory=dict)


class AgentErrorEvent(BaseEvent):
    """Emitted when an agent encounters an error."""

    event_type: EventType = EventType.AGENT_ERROR
    data: dict[str, Any]  # Must include 'error' and optionally 'traceback'


class ThinkingEvent(BaseEvent):
    """Emitted for streaming agent reasoning/thinking."""

    event_type: EventType = EventType.THINKING
    data: dict[str, str]  # Must include 'content' (streaming text)


class ToolCallStartEvent(BaseEvent):
    """Emitted when an agent invokes a tool."""

    event_type: EventType = EventType.TOOL_CALL_START
    data: dict[str, Any]  # Includes 'tool_name', 'input'


class ToolCallResultEvent(BaseEvent):
    """Emitted with tool invocation result."""

    event_type: EventType = EventType.TOOL_CALL_RESULT
    data: dict[str, Any]  # Includes 'tool_name', 'output', 'duration_ms'


class FindingDiscoveredEvent(BaseEvent):
    """Emitted when an agent discovers a finding."""

    event_type: EventType = EventType.FINDING_DISCOVERED
    data: dict[str, Any]  # Includes 'finding_id', 'category', 'severity', 'line', 'description'


class FindingsConsolidatedEvent(BaseEvent):
    """Emitted when coordinator merges findings."""

    event_type: EventType = EventType.FINDINGS_CONSOLIDATED
    data: dict[str, Any]  # Includes 'total_findings', 'by_severity'


class PlanCreatedEvent(BaseEvent):
    """Emitted when coordinator creates execution plan."""

    event_type: EventType = EventType.PLAN_CREATED
    agent_id: AgentType = AgentType.COORDINATOR
    data: dict[str, Any]  # Includes 'plan_steps' (list)


class AgentDelegatedEvent(BaseEvent):
    """Emitted when coordinator delegates to specialist."""

    event_type: EventType = EventType.AGENT_DELEGATED
    agent_id: AgentType = AgentType.COORDINATOR
    data: dict[str, Any]  # Includes 'delegated_to', 'task'


class FinalReportEvent(BaseEvent):
    """Emitted when review is complete."""

    event_type: EventType = EventType.FINAL_REPORT
    agent_id: AgentType = AgentType.COORDINATOR
    data: dict[str, Any]  # Includes full review report


class FixProposedEvent(BaseEvent):
    """Emitted when an agent proposes a fix."""

    event_type: EventType = EventType.FIX_PROPOSED
    data: dict[
        str, Any
    ]  # Includes 'finding_id', 'original_code', 'proposed_fix', 'explanation', 'confidence'


class FixVerifiedEvent(BaseEvent):
    """Emitted when a proposed fix is verified."""

    event_type: EventType = EventType.FIX_VERIFIED
    data: dict[
        str, Any
    ]  # Includes 'finding_id', 'verification_passed', 'test_output', 'duration_ms'


# Union type for all events
Event = (
    AgentStartedEvent
    | AgentCompletedEvent
    | AgentErrorEvent
    | ThinkingEvent
    | ToolCallStartEvent
    | ToolCallResultEvent
    | FindingDiscoveredEvent
    | FindingsConsolidatedEvent
    | PlanCreatedEvent
    | AgentDelegatedEvent
    | FinalReportEvent
    | FixProposedEvent
    | FixVerifiedEvent
)


class Finding(BaseModel):
    """A single security or bug finding."""

    finding_id: str
    category: str  # e.g., "sql_injection", "null_reference", "hardcoded_secret"
    severity: Severity
    line: int
    description: str
    agent_id: AgentType


class AgentResult(BaseModel):
    """Result returned by an agent after analysis."""

    agent_id: AgentType
    findings: list[Finding] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
