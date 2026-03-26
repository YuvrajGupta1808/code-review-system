"""Tests for agents B6, B8, B9."""

import pytest
from unittest.mock import AsyncMock

from backend.agents.security import SecurityAgent
from backend.agents.bug import BugAgent
from backend.llm_client import (
    ThinkingChunk,
    TextChunk,
    ToolCallChunk,
    ToolCallResultChunk,
)
from backend.models import (
    AgentType,
    EventType,
    Severity,
)


@pytest.mark.asyncio
async def test_security_agent_basic_instantiation():
    """Test SecurityAgent can be created with mock LLM."""
    mock_llm = AsyncMock()
    agent = SecurityAgent(llm_client=mock_llm)
    assert agent.agent_id == AgentType.SECURITY


@pytest.mark.asyncio
async def test_bug_agent_basic_instantiation():
    """Test BugAgent can be created with mock LLM."""
    mock_llm = AsyncMock()
    agent = BugAgent(llm_client=mock_llm)
    assert agent.agent_id == AgentType.BUG_DETECTION


@pytest.mark.asyncio
async def test_security_agent_event_sequence():
    """Test SecurityAgent emits events in correct order."""
    mock_llm = AsyncMock()

    async def mock_stream(*args, **kwargs):
        # Thinking
        yield ThinkingChunk(delta="Checking for SQL injection...")
        # Tool call
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='{"category": "sql_injection", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"severity": "high", "line_number": 10, ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"description": "SQL injection vulnerability", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"code_snippet": "query = f\'SELECT * FROM users WHERE id={user_id}\'", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"fix_suggestion": "Use parameterized queries with placeholders"}',
        )
        yield ToolCallResultChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_json='{"category": "sql_injection", "severity": "high", "line_number": 10, '
            '"description": "SQL injection vulnerability", '
            '"code_snippet": "query = f\'SELECT * FROM users WHERE id={user_id}\'", '
            '"fix_suggestion": "Use parameterized queries with placeholders"}',
        )

    mock_llm.stream_completion = mock_stream
    agent = SecurityAgent(llm_client=mock_llm)

    events = []

    async def collect_event(event):
        events.append(event)

    result = await agent.analyze("test code", {}, collect_event)

    # Verify event order
    event_types = [e.event_type for e in events]
    assert event_types[0] == EventType.AGENT_STARTED
    assert event_types[-1] == EventType.AGENT_COMPLETED
    assert EventType.THINKING in event_types
    assert EventType.TOOL_CALL_START in event_types
    assert EventType.TOOL_CALL_RESULT in event_types
    assert EventType.FINDING_DISCOVERED in event_types

    # Verify findings
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.category == "sql_injection"
    assert finding.severity == Severity.HIGH
    assert finding.line == 10
    assert finding.agent_id == AgentType.SECURITY


@pytest.mark.asyncio
async def test_bug_agent_event_sequence():
    """Test BugAgent emits events in correct order."""
    mock_llm = AsyncMock()

    async def mock_stream(*args, **kwargs):
        yield ThinkingChunk(delta="Looking for null reference...")
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='{"category": "null_reference", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"severity": "high", "line_number": 5, ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"description": "Potential null dereference", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"code_snippet": "obj.method()", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"fix_suggestion": "Add null check before calling method"}',
        )
        yield ToolCallResultChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_json='{"category": "null_reference", "severity": "high", "line_number": 5, '
            '"description": "Potential null dereference", "code_snippet": "obj.method()", '
            '"fix_suggestion": "Add null check before calling method"}',
        )

    mock_llm.stream_completion = mock_stream
    agent = BugAgent(llm_client=mock_llm)

    events = []

    async def collect_event(event):
        events.append(event)

    result = await agent.analyze("test code", {}, collect_event)

    # Verify findings
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.category == "null_reference"
    assert finding.agent_id == AgentType.BUG_DETECTION


@pytest.mark.asyncio
async def test_agent_multiple_findings():
    """Test agent with multiple findings."""
    mock_llm = AsyncMock()

    async def mock_stream(*args, **kwargs):
        # First finding
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='{"category": "hardcoded_secret", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"severity": "critical", "line_number": 1, ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"description": "API key in code", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"code_snippet": "API_KEY = \'sk_live_123456\'", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"fix_suggestion": "Use environment variables"}',
        )
        yield ToolCallResultChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_json='{"category": "hardcoded_secret", "severity": "critical", "line_number": 1, '
            '"description": "API key in code", "code_snippet": "API_KEY = \'sk_live_123456\'", '
            '"fix_suggestion": "Use environment variables"}',
        )

        # Second finding
        yield ToolCallChunk(
            tool_call_id="call_2", tool_name="report_finding", args_delta='{"category": "xss", '
        )
        yield ToolCallChunk(
            tool_call_id="call_2",
            tool_name="report_finding",
            args_delta='"severity": "high", "line_number": 15, ',
        )
        yield ToolCallChunk(
            tool_call_id="call_2",
            tool_name="report_finding",
            args_delta='"description": "Unescaped HTML injection", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_2",
            tool_name="report_finding",
            args_delta='"code_snippet": "html = f\'<div>{user_input}</div>\'", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_2",
            tool_name="report_finding",
            args_delta='"fix_suggestion": "Escape user input"}',
        )
        yield ToolCallResultChunk(
            tool_call_id="call_2",
            tool_name="report_finding",
            args_json='{"category": "xss", "severity": "high", "line_number": 15, '
            '"description": "Unescaped HTML injection", "code_snippet": "html = f\'<div>{user_input}</div>\'", '
            '"fix_suggestion": "Escape user input"}',
        )

    mock_llm.stream_completion = mock_stream
    agent = SecurityAgent(llm_client=mock_llm)

    events = []

    async def collect_event(event):
        events.append(event)

    result = await agent.analyze("test code", {}, collect_event)

    # Verify multiple findings
    assert len(result.findings) == 2
    assert result.findings[0].category == "hardcoded_secret"
    assert result.findings[1].category == "xss"


@pytest.mark.asyncio
async def test_agent_with_fix_proposed():
    """Test that fix_proposed event is emitted when fix_suggestion is provided."""
    mock_llm = AsyncMock()

    async def mock_stream(*args, **kwargs):
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='{"category": "hardcoded_secret", "severity": "critical", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"line_number": 5, "description": "Password in code", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"code_snippet": "password = \'secret123\'", ',
        )
        yield ToolCallChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_delta='"fix_suggestion": "password = os.getenv(\'APP_PASSWORD\')"}',
        )
        yield ToolCallResultChunk(
            tool_call_id="call_1",
            tool_name="report_finding",
            args_json='{"category": "hardcoded_secret", "severity": "critical", "line_number": 5, '
            '"description": "Password in code", "code_snippet": "password = \'secret123\'", '
            '"fix_suggestion": "password = os.getenv(\'APP_PASSWORD\')"}',
        )

    mock_llm.stream_completion = mock_stream
    agent = SecurityAgent(llm_client=mock_llm)

    events = []

    async def collect_event(event):
        events.append(event)

    await agent.analyze("test code", {}, collect_event)

    # Find fix_proposed event
    fix_events = [e for e in events if e.event_type == EventType.FIX_PROPOSED]
    assert len(fix_events) == 1
    assert fix_events[0].data["proposed_fix"] == "password = os.getenv('APP_PASSWORD')"


@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test agent handles errors gracefully."""
    mock_llm = AsyncMock()

    async def mock_stream_error(*args, **kwargs):
        # Make this raise inside the generator
        if False:
            yield
        raise Exception("LLM connection failed")

    mock_llm.stream_completion = mock_stream_error

    agent = SecurityAgent(llm_client=mock_llm)
    events = []

    async def collect_event(event):
        events.append(event)

    with pytest.raises(Exception):
        await agent.analyze("test code", {}, collect_event)

    # Verify error event was emitted
    error_events = [e for e in events if e.event_type == EventType.AGENT_ERROR]
    assert len(error_events) == 1
    assert "LLM connection failed" in error_events[0].data["error"]


@pytest.mark.asyncio
async def test_thinking_streaming():
    """Test thinking/reasoning content is streamed properly."""
    mock_llm = AsyncMock()

    async def mock_stream(*args, **kwargs):
        yield ThinkingChunk(delta="Step 1: ")
        yield ThinkingChunk(delta="Analyzing ")
        yield ThinkingChunk(delta="the code ")
        yield ThinkingChunk(delta="structure. ")
        yield TextChunk(delta="Found issue")

    mock_llm.stream_completion = mock_stream
    agent = SecurityAgent(llm_client=mock_llm)

    events = []

    async def collect_event(event):
        events.append(event)

    await agent.analyze("test code", {}, collect_event)

    # Verify thinking events
    thinking_events = [e for e in events if e.event_type == EventType.THINKING]
    assert len(thinking_events) > 0
    thinking_content = "".join([e.data["content"] for e in thinking_events])
    assert "Analyzing" in thinking_content
    assert "code" in thinking_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
