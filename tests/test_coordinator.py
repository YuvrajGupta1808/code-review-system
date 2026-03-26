"""Tests for CoordinatorAgent with LangGraph."""

import pytest
from unittest.mock import AsyncMock

from backend.agents.coordinator import CoordinatorAgent
from backend.models import (
    AgentType,
    EventType,
    Severity,
    Finding,
    AgentResult,
)


@pytest.mark.asyncio
async def test_coordinator_instantiation():
    """Test CoordinatorAgent can be created."""
    coordinator = CoordinatorAgent(specialists=[])
    assert coordinator.agent_id == AgentType.COORDINATOR


@pytest.mark.asyncio
async def test_coordinator_with_no_specialists():
    """Test coordinator runs with no specialists."""
    coordinator = CoordinatorAgent()
    events = []

    async def collect_event(event):
        events.append(event)

    result = await coordinator.analyze("x = 1", {}, collect_event)

    assert result.agent_id == AgentType.COORDINATOR
    event_types = [e.event_type for e in events]
    assert EventType.AGENT_STARTED in event_types
    assert EventType.PLAN_CREATED in event_types


@pytest.mark.asyncio
async def test_coordinator_plan_structure():
    """Test coordinator creates proper execution plan."""
    mock_sec = AsyncMock()
    mock_sec.agent_id = AgentType.SECURITY
    mock_sec.analyze = AsyncMock(return_value=AgentResult(agent_id=AgentType.SECURITY, findings=[]))

    coordinator = CoordinatorAgent(specialists=[mock_sec])
    events = []

    async def collect_event(event):
        events.append(event)

    await coordinator.analyze("test code", {}, collect_event)

    # Find plan event
    plan_events = [e for e in events if e.event_type == EventType.PLAN_CREATED]
    assert len(plan_events) == 1

    plan_steps = plan_events[0].data["plan_steps"]

    # Check plan structure
    assert len(plan_steps) >= 3  # parse_code + security + consolidate
    assert plan_steps[0]["action"] == "parse_code"

    actions = [s["action"] for s in plan_steps]
    assert "consolidate" in actions


@pytest.mark.asyncio
async def test_coordinator_with_mock_specialist():
    """Test coordinator delegates to specialist and consolidates findings."""
    # Create mock specialist
    mock_specialist = AsyncMock()
    mock_specialist.agent_id = AgentType.SECURITY

    finding = Finding(
        finding_id="test_1",
        category="sql_injection",
        severity=Severity.HIGH,
        line=10,
        description="Test finding",
        agent_id=AgentType.SECURITY,
    )

    mock_specialist.analyze = AsyncMock(
        return_value=AgentResult(agent_id=AgentType.SECURITY, findings=[finding])
    )

    coordinator = CoordinatorAgent(specialists=[mock_specialist])
    events = []

    async def collect_event(event):
        events.append(event)

    result = await coordinator.analyze("test code", {}, collect_event)

    # Verify delegation happened
    delegated_events = [e for e in events if e.event_type == EventType.AGENT_DELEGATED]
    assert len(delegated_events) == 1
    assert delegated_events[0].data["delegated_to"] == AgentType.SECURITY.value

    # Verify finding was consolidated
    assert len(result.findings) == 1
    assert result.findings[0].category == "sql_injection"


@pytest.mark.asyncio
async def test_coordinator_consolidates_duplicate_findings():
    """Test coordinator deduplicates findings by (category, line)."""
    coordinator = CoordinatorAgent()

    # Two specialists report same issue at same line
    result1 = AgentResult(
        agent_id=AgentType.SECURITY,
        findings=[
            Finding(
                finding_id="sec_1",
                category="sql_injection",
                severity=Severity.CRITICAL,
                line=10,
                description="Critical SQL injection",
                agent_id=AgentType.SECURITY,
            )
        ],
    )

    result2 = AgentResult(
        agent_id=AgentType.BUG_DETECTION,
        findings=[
            Finding(
                finding_id="bug_1",
                category="sql_injection",
                severity=Severity.HIGH,
                line=10,
                description="High SQL injection",
                agent_id=AgentType.BUG_DETECTION,
            ),
            Finding(
                finding_id="bug_2",
                category="null_reference",
                severity=Severity.MEDIUM,
                line=20,
                description="Null reference",
                agent_id=AgentType.BUG_DETECTION,
            ),
        ],
    )

    consolidated, conflicts = coordinator._consolidate_findings([result1, result2])

    # Should have 2 findings (duplicate at line 10 removed)
    assert len(consolidated) == 2
    assert conflicts == 1

    # Check highest severity is kept
    sql_inj = [f for f in consolidated if f.category == "sql_injection"][0]
    assert sql_inj.severity == Severity.CRITICAL
    assert sql_inj.finding_id == "sec_1"


@pytest.mark.asyncio
async def test_coordinator_emits_findings_consolidated():
    """Test coordinator emits findings_consolidated event."""
    mock_specialist = AsyncMock()
    mock_specialist.agent_id = AgentType.SECURITY

    finding = Finding(
        finding_id="1",
        category="xss",
        severity=Severity.HIGH,
        line=5,
        description="XSS vulnerability",
        agent_id=AgentType.SECURITY,
    )

    mock_specialist.analyze = AsyncMock(
        return_value=AgentResult(agent_id=AgentType.SECURITY, findings=[finding])
    )

    coordinator = CoordinatorAgent(specialists=[mock_specialist])
    events = []

    async def collect_event(event):
        events.append(event)

    await coordinator.analyze("test", {}, collect_event)

    # Find consolidated event
    consolidated_events = [e for e in events if e.event_type == EventType.FINDINGS_CONSOLIDATED]
    assert len(consolidated_events) == 1

    data = consolidated_events[0].data
    assert data["total_findings"] == 1
    assert data["by_severity"]["high"] == 1


@pytest.mark.asyncio
async def test_coordinator_emits_final_report():
    """Test coordinator emits final_report event with summary."""
    mock_specialist = AsyncMock()
    mock_specialist.agent_id = AgentType.SECURITY

    findings = [
        Finding(
            finding_id="1",
            category="sql_injection",
            severity=Severity.CRITICAL,
            line=1,
            description="desc",
            agent_id=AgentType.SECURITY,
        ),
        Finding(
            finding_id="2",
            category="xss",
            severity=Severity.HIGH,
            line=5,
            description="desc",
            agent_id=AgentType.SECURITY,
        ),
    ]

    mock_specialist.analyze = AsyncMock(
        return_value=AgentResult(agent_id=AgentType.SECURITY, findings=findings)
    )

    coordinator = CoordinatorAgent(specialists=[mock_specialist])
    events = []

    async def collect_event(event):
        events.append(event)

    await coordinator.analyze("test", {}, collect_event)

    # Find final report
    report_events = [e for e in events if e.event_type == EventType.FINAL_REPORT]
    assert len(report_events) == 1

    report = report_events[0].data
    assert "Code review complete" in report["summary"]
    assert report["total_findings"] == 2
    assert len(report["critical_findings"]) == 1


@pytest.mark.asyncio
async def test_coordinator_parses_code():
    """Test coordinator correctly parses code structure."""
    coordinator = CoordinatorAgent()

    code = """
import os
from collections import defaultdict

class DataProcessor:
    def __init__(self):
        pass

    def process(self):
        pass

    def validate(self):
        pass

def helper_function():
    pass

def main():
    pass
"""

    metadata = coordinator._parse_code(code)

    assert metadata["classes"] == 1
    assert metadata["functions"] >= 4  # main, helper, + methods
    assert metadata["imports"] == 2
    assert metadata["lines"] >= 19


@pytest.mark.asyncio
async def test_coordinator_handles_syntax_error():
    """Test coordinator handles invalid code gracefully."""
    coordinator = CoordinatorAgent()
    invalid_code = "def broken(: pass"

    metadata = coordinator._parse_code(invalid_code)

    # Should still have basic metadata
    assert "lines" in metadata
    assert metadata["functions"] == 0
    assert metadata["classes"] == 0


@pytest.mark.asyncio
async def test_coordinator_severity_ranking():
    """Test severity ranking for deduplication."""
    coordinator = CoordinatorAgent()

    assert coordinator._severity_rank(Severity.CRITICAL) > coordinator._severity_rank(Severity.HIGH)
    assert coordinator._severity_rank(Severity.HIGH) > coordinator._severity_rank(Severity.MEDIUM)
    assert coordinator._severity_rank(Severity.MEDIUM) > coordinator._severity_rank(Severity.LOW)
    assert coordinator._severity_rank(Severity.LOW) > coordinator._severity_rank(Severity.INFO)


@pytest.mark.asyncio
async def test_coordinator_count_by_severity():
    """Test counting findings by severity."""
    coordinator = CoordinatorAgent()

    findings = [
        Finding(
            finding_id="1",
            category="a",
            severity=Severity.CRITICAL,
            line=1,
            description="d",
            agent_id=AgentType.SECURITY,
        ),
        Finding(
            finding_id="2",
            category="b",
            severity=Severity.CRITICAL,
            line=2,
            description="d",
            agent_id=AgentType.SECURITY,
        ),
        Finding(
            finding_id="3",
            category="c",
            severity=Severity.HIGH,
            line=3,
            description="d",
            agent_id=AgentType.BUG_DETECTION,
        ),
        Finding(
            finding_id="4",
            category="d",
            severity=Severity.MEDIUM,
            line=4,
            description="d",
            agent_id=AgentType.BUG_DETECTION,
        ),
        Finding(
            finding_id="5",
            category="e",
            severity=Severity.LOW,
            line=5,
            description="d",
            agent_id=AgentType.SECURITY,
        ),
    ]

    counts = coordinator._count_by_severity(findings)

    assert counts["critical"] == 2
    assert counts["high"] == 1
    assert counts["medium"] == 1
    assert counts["low"] == 1
    assert counts["info"] == 0


@pytest.mark.asyncio
async def test_coordinator_event_sequence():
    """Test coordinator emits events in correct order."""
    mock_specialist = AsyncMock()
    mock_specialist.agent_id = AgentType.SECURITY
    mock_specialist.analyze = AsyncMock(
        return_value=AgentResult(agent_id=AgentType.SECURITY, findings=[])
    )

    coordinator = CoordinatorAgent(specialists=[mock_specialist])
    events = []

    async def collect_event(event):
        events.append(event)

    await coordinator.analyze("x = 1", {}, collect_event)

    event_types = [e.event_type for e in events]

    # Verify sequence
    assert event_types[0] == EventType.AGENT_STARTED
    assert EventType.PLAN_CREATED in event_types
    assert EventType.AGENT_DELEGATED in event_types
    assert EventType.FINDINGS_CONSOLIDATED in event_types
    assert EventType.FINAL_REPORT in event_types
    assert event_types[-1] == EventType.AGENT_COMPLETED


@pytest.mark.asyncio
async def test_coordinator_with_multiple_specialists():
    """Test coordinator with multiple specialist agents."""
    mock_sec = AsyncMock()
    mock_sec.agent_id = AgentType.SECURITY
    mock_sec.analyze = AsyncMock(
        return_value=AgentResult(
            agent_id=AgentType.SECURITY,
            findings=[
                Finding(
                    finding_id="1",
                    category="sql_injection",
                    severity=Severity.CRITICAL,
                    line=5,
                    description="desc",
                    agent_id=AgentType.SECURITY,
                )
            ],
        )
    )

    mock_bug = AsyncMock()
    mock_bug.agent_id = AgentType.BUG_DETECTION
    mock_bug.analyze = AsyncMock(
        return_value=AgentResult(
            agent_id=AgentType.BUG_DETECTION,
            findings=[
                Finding(
                    finding_id="2",
                    category="null_reference",
                    severity=Severity.HIGH,
                    line=10,
                    description="desc",
                    agent_id=AgentType.BUG_DETECTION,
                )
            ],
        )
    )

    coordinator = CoordinatorAgent(specialists=[mock_sec, mock_bug])
    events = []

    async def collect_event(event):
        events.append(event)

    result = await coordinator.analyze("test code", {}, collect_event)

    # Verify both specialists delegated
    delegated = [e for e in events if e.event_type == EventType.AGENT_DELEGATED]
    assert len(delegated) == 2

    # Verify both findings consolidated
    assert len(result.findings) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
