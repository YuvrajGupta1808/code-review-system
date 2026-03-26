# Streaming Events Specification

This document defines all event types, their structure, and semantics for the Code Review System event bus.

## Overview

All events share a common structure:

```json
{
  "event_type": "agent_started",
  "agent_id": "coordinator",
  "timestamp": "2026-03-25T14:30:45.123456Z",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {}
}
```

### Fields

- **event_type** (string): Type of event (enum: see Event Types below)
- **agent_id** (string): Which agent emitted the event (`coordinator`, `security_agent`, `bug_agent`)
- **timestamp** (string): ISO 8601 UTC timestamp
- **event_id** (string): Unique event identifier (UUID)
- **data** (object): Event-specific payload structure (see detailed schemas below)

---

## Event Types

### Agent Lifecycle

#### `agent_started`

Emitted when an agent begins analysis.

```json
{
  "event_type": "agent_started",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T14:30:45.123456Z",
  "event_id": "...",
  "data": {}
}
```

**Data fields:** (none required; optional metadata may be included)

---

#### `agent_completed`

Emitted when an agent finishes analysis.

```json
{
  "event_type": "agent_completed",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T14:30:50.654321Z",
  "event_id": "...",
  "data": {
    "findings_count": 3,
    "duration_ms": 5531
  }
}
```

**Data fields:**
- `findings_count` (integer, optional): Number of findings discovered
- `duration_ms` (integer, optional): Time taken for analysis

---

#### `agent_error`

Emitted when an agent encounters an error.

```json
{
  "event_type": "agent_error",
  "agent_id": "bug_agent",
  "timestamp": "2026-03-25T14:30:52.000000Z",
  "event_id": "...",
  "data": {
    "error": "Analysis timeout after 30 seconds",
    "traceback": "(optional stack trace)"
  }
}
```

**Data fields:**
- `error` (string, required): Error message
- `traceback` (string, optional): Full error traceback for debugging

---

### Reasoning and Tool Use

#### `thinking`

Emitted for streaming agent reasoning (like extended thinking).

```json
{
  "event_type": "thinking",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T14:30:46.000000Z",
  "event_id": "...",
  "data": {
    "content": "I notice line 45 has a SQL query built with string concatenation. "
  }
}
```

**Data fields:**
- `content` (string, required): Incremental reasoning text (append this to the stream)

**Note:** Multiple `thinking` events form a continuous stream; concatenate the `content` field to reconstruct the full reasoning.

---

#### `tool_call_start`

Emitted when an agent invokes a tool.

```json
{
  "event_type": "tool_call_start",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T14:30:47.000000Z",
  "event_id": "...",
  "data": {
    "tool_name": "code_executor",
    "input": {
      "code": "SELECT * FROM users WHERE id = {user_id}"
    }
  }
}
```

**Data fields:**
- `tool_name` (string, required): Name of the tool being invoked
- `input` (object, required): Tool input arguments

---

#### `tool_call_result`

Emitted with tool invocation result.

```json
{
  "event_type": "tool_call_result",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T14:30:47.500000Z",
  "event_id": "...",
  "data": {
    "tool_name": "code_executor",
    "output": "SQL Injection vulnerability confirmed",
    "duration_ms": 234
  }
}
```

**Data fields:**
- `tool_name` (string, required): Name of the tool (must match preceding `tool_call_start`)
- `output` (any, required): Tool output (string, object, or list)
- `duration_ms` (integer, required): Execution time in milliseconds

---

### Findings

#### `finding_discovered`

Emitted when an agent discovers a finding.

```json
{
  "event_type": "finding_discovered",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T14:30:48.000000Z",
  "event_id": "...",
  "data": {
    "finding_id": "sqli_001",
    "category": "sql_injection",
    "severity": "critical",
    "line": 45,
    "description": "User input directly concatenated into SQL query without parameterization"
  }
}
```

**Data fields:**
- `finding_id` (string, required): Unique identifier for this finding
- `category` (string, required): Issue type (e.g., `sql_injection`, `null_reference`, `hardcoded_secret`, `xss`, `race_condition`)
- `severity` (string, required): One of `critical`, `high`, `medium`, `low`, `info`
- `line` (integer, required): Line number in source code where issue occurs
- `description` (string, required): Human-readable description of the issue

---

#### `findings_consolidated`

Emitted when coordinator merges findings from all agents.

```json
{
  "event_type": "findings_consolidated",
  "agent_id": "coordinator",
  "timestamp": "2026-03-25T14:30:52.000000Z",
  "event_id": "...",
  "data": {
    "total_findings": 5,
    "by_severity": {
      "critical": 1,
      "high": 2,
      "medium": 2,
      "low": 0,
      "info": 0
    },
    "conflicts_resolved": 0
  }
}
```

**Data fields:**
- `total_findings` (integer, required): Total deduplicated findings
- `by_severity` (object, required): Count of findings per severity level
- `conflicts_resolved` (integer, optional): Number of conflicting findings that were merged/resolved

---

### Coordinator Workflow

#### `plan_created`

Emitted when coordinator creates execution plan.

```json
{
  "event_type": "plan_created",
  "agent_id": "coordinator",
  "timestamp": "2026-03-25T14:30:45.500000Z",
  "event_id": "...",
  "data": {
    "plan_steps": [
      {
        "step": 1,
        "action": "parse_code",
        "description": "Parse code structure"
      },
      {
        "step": 2,
        "action": "security_analysis",
        "description": "Run security analysis in parallel with bug detection",
        "parallel_with": [3]
      },
      {
        "step": 3,
        "action": "bug_analysis",
        "description": "Run bug detection in parallel with security analysis",
        "parallel_with": [2]
      },
      {
        "step": 4,
        "action": "consolidate",
        "description": "Consolidate findings"
      }
    ]
  }
}
```

**Data fields:**
- `plan_steps` (array, required): List of planned steps with step number, action, and description

---

#### `agent_delegated`

Emitted when coordinator delegates to specialist.

```json
{
  "event_type": "agent_delegated",
  "agent_id": "coordinator",
  "timestamp": "2026-03-25T14:30:45.600000Z",
  "event_id": "...",
  "data": {
    "delegated_to": "security_agent",
    "task": "Perform security analysis on provided code"
  }
}
```

**Data fields:**
- `delegated_to` (string, required): Agent ID being delegated to
- `task` (string, required): Task description

---

### Results

#### `final_report`

Emitted when review is complete.

```json
{
  "event_type": "final_report",
  "agent_id": "coordinator",
  "timestamp": "2026-03-25T14:30:53.000000Z",
  "event_id": "...",
  "data": {
    "summary": "Code review complete. Found 5 issues.",
    "total_findings": 5,
    "critical_findings": [
      {
        "finding_id": "sqli_001",
        "category": "sql_injection",
        "severity": "critical",
        "line": 45,
        "description": "SQL injection vulnerability"
      }
    ],
    "fixes_proposed": 3,
    "fixes_verified": 2
  }
}
```

**Data fields:**
- `summary` (string, required): Executive summary of review results
- `total_findings` (integer, required): Total number of findings
- `critical_findings` (array, optional): List of critical severity findings
- `fixes_proposed` (integer, optional): Count of proposed fixes
- `fixes_verified` (integer, optional): Count of verified fixes

---

### Fixes

#### `fix_proposed`

Emitted when an agent proposes a fix.

```json
{
  "event_type": "fix_proposed",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T14:30:49.000000Z",
  "event_id": "...",
  "data": {
    "finding_id": "sqli_001",
    "original_code": "query = f'SELECT * FROM users WHERE id = {user_id}'",
    "proposed_fix": "query = 'SELECT * FROM users WHERE id = ?'\ncursor.execute(query, (user_id,))",
    "explanation": "Use parameterized queries to prevent SQL injection attacks",
    "confidence": 0.95
  }
}
```

**Data fields:**
- `finding_id` (string, required): ID of finding this fix addresses
- `original_code` (string, required): Original problematic code snippet
- `proposed_fix` (string, required): Fixed code
- `explanation` (string, required): Why this fix resolves the issue
- `confidence` (float, required): Confidence in the fix (0.0 to 1.0)

---

#### `fix_verified`

Emitted when a proposed fix is verified.

```json
{
  "event_type": "fix_verified",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T14:30:50.000000Z",
  "event_id": "...",
  "data": {
    "finding_id": "sqli_001",
    "verification_passed": true,
    "test_output": "Parameterized query executed without errors",
    "duration_ms": 156
  }
}
```

**Data fields:**
- `finding_id` (string, required): ID of fix being verified
- `verification_passed` (boolean, required): Whether verification succeeded
- `test_output` (string, required): Output from verification process
- `duration_ms` (integer, required): Verification duration in milliseconds

---

## Event Bus Guarantees

1. **Ordering**: Events from a single agent arrive in order at all subscribers
2. **Concurrency**: Multiple agents may emit events simultaneously
3. **Reliability**: No events are dropped under normal load
4. **Latency**: Events are published immediately (no batching)

---

## Transport

Events are transmitted via:
- **WebSocket**: `/ws/review` endpoint (preferred)
- **Server-Sent Events (SSE)**: `/stream/review` endpoint

Each event is serialized as JSON and sent immediately upon emission.
