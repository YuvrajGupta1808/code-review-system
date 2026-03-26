# Agent Architecture

## Overview

The code review system uses a **hierarchical agent architecture** with LangGraph orchestration:

```
┌─────────────────────────────────────────────────────────┐
│          CoordinatorAgent (LangGraph)                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │ parse_code → create_plan → [delegate specialists]│  │
│  │ → consolidate_findings → final_report            │  │
│  └──────────────────────────────────────────────────┘  │
│                      │                                  │
│  ┌───────────────────┼───────────────────┐            │
│  ▼                   ▼                   ▼            │
│  SecurityAgent    BugAgent             (Optional)     │
│  (LLM Streaming)  (LLM Streaming)      Extra Agents   │
│  ↓                ↓                                    │
│  [Findings]       [Findings]                          │
│                                                       │
└─────────────────────────────────────────────────────────┘
```

## Agents

### 1. **CoordinatorAgent** (LangGraph StateGraph)

**File:** `backend/agents/coordinator.py`

Orchestrates the entire code review workflow:

- **State Schema:** `CoordinatorState` with code, context, findings, metadata
- **Nodes:**
  1. `parse_code` — Analyze code structure using AST
  2. `create_plan` — Build execution plan (emits `plan_created`)
  3. `delegate_to_specialists` — Fan-out to specialists using **Send API**
  4. `run_specialist` — Execute each specialist concurrently
  5. `consolidate` — Merge findings from specialists (deduplicate by category+line)
  6. `final_report` — Generate review summary

**Event Emission:**
- `agent_started` — Workflow begins
- `plan_created` — With execution plan steps
- `agent_delegated` — When delegating to each specialist
- `findings_consolidated` — After merging specialist results
- `final_report` — Review complete with summary
- `agent_completed` — With duration and finding count

**Key Features:**
- Uses **Send API** for parallel specialist execution
- **Reducer on `specialist_results`** to accumulate findings from multiple agents
- Deduplicates findings by `(category, line)`, keeping highest severity
- Counts conflicts resolved during consolidation

### 2. **SecurityAgent** (Direct LLM Streaming)

**File:** `backend/agents/security_agent.py`

Specialist agent for vulnerability detection:

- **LLM Tool:** `report_finding` function for structured findings
- **Focuses on:**
  - SQL injection
  - Hardcoded secrets
  - Command injection
  - XSS vulnerabilities
  - Auth/authorization flaws
  - Unsafe deserialization

**Event Emission:**
- `agent_started` — Analysis begins
- `thinking` (streaming) — Model reasoning as it arrives
- `tool_call_start` / `tool_call_result` — Each finding reported
- `finding_discovered` — Structured finding event
- `fix_proposed` — When a fix suggestion is available (optional)
- `agent_completed` — Analysis done

### 3. **BugAgent** (Direct LLM Streaming)

**File:** `backend/agents/bug_agent.py`

Specialist agent for bug detection:

- **LLM Tool:** `report_finding` function for structured findings
- **Focuses on:**
  - Null/None dereferences
  - Logic errors
  - Type mismatches
  - Race conditions
  - Resource leaks
  - Error handling gaps

**Event Emission:** Same as SecurityAgent

### 4. **BaseAgent** (Abstract Interface)

**File:** `backend/agents/base.py`

Abstract base class defining the agent contract:

```python
class BaseAgent(ABC):
    async def analyze(
        self,
        code: str,
        context: dict[str, Any],
        event_callback: Callable[[BaseEvent], Any],
    ) -> AgentResult:
        """Analyze code and emit events."""
```

**Key Points:**
- All agents share this interface
- Implementations can use LangGraph (Coordinator) or direct LLM streaming (Specialists)
- Events are emitted via callback for real-time UI streaming
- Returns `AgentResult` with findings, errors, and metadata

## Data Flow

### Coordinator Workflow

```
Code Input
    ↓
┌─────────────────────────────────────────┐
│ 1. Parse Code (AST analysis)            │
│    → code_metadata (lines, functions...)│
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 2. Create Plan (execution steps)        │
│    → emit plan_created event            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 3. Delegate to Specialists (Parallel)   │
│    → SecurityAgent.analyze()            │
│    → BugAgent.analyze()                 │
│    (each emits thinking, findings, etc) │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 4. Consolidate Findings                 │
│    → deduplicate by (category, line)    │
│    → keep highest severity              │
│    → emit findings_consolidated         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 5. Final Report                         │
│    → summary + critical findings        │
│    → emit final_report event            │
└─────────────────────────────────────────┘
    ↓
AgentResult (consolidated findings)
```

### Specialist Workflow (SecurityAgent/BugAgent)

```
Code Input
    ↓
emit agent_started
    ↓
Stream from LLM:
├── emit thinking (reasoning chunks)
├── detect tool call (report_finding)
├── emit tool_call_start
├── accumulate tool args
├── emit tool_call_result
├── parse finding
├── emit finding_discovered
└── repeat for each finding
    ↓
emit agent_completed
    ↓
Return AgentResult(findings=[...])
```

## Event Types

All agents emit these core events:

- **`agent_started`** — Analysis begins
- **`thinking`** — Streaming reasoning/analysis (specialist only)
- **`tool_call_start`** — Agent invokes a tool
- **`tool_call_result`** — Tool execution completes
- **`finding_discovered`** — Issue identified (category, severity, line)
- **`agent_completed`** — Analysis done
- **`agent_error`** — Analysis failed

Coordinator-specific:

- **`plan_created`** — Execution plan with steps
- **`agent_delegated`** — Delegating to specialist
- **`findings_consolidated`** — Merged results from all specialists
- **`final_report`** — Review complete with summary

## LLM Integration

**Provider:** MiniMax (OpenAI-compatible)

**Key Features:**
- Uses `reasoning_split` for streaming thinking
- Tool-based findings discovery
- Structured JSON parsing for findings

**Environment:**
```
OPENAI_BASE_URL=https://api.minimax.io/v1
OPENAI_API_KEY=<your-api-key>
```

**Alternative (Anthropic-compatible):**
```
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_API_KEY=<your-api-key>
```

## LangGraph Benefits

The Coordinator uses LangGraph for:

1. **State Management** — Centralized workflow state with TypedDict
2. **Parallel Execution** — Send API for concurrent specialists
3. **Accumulation** — Reducers on `specialist_results` field
4. **Clear Flow** — Explicit edges between workflow steps
5. **Event Integration** — Each node can emit events via callback closure

## Extending the System

### Add a New Specialist Agent

1. Create `backend/agents/new_agent.py` with a class inheriting `BaseAgent`
2. Implement `analyze()` method (use LLMClient for LLM streaming)
3. Emit events: `agent_started` → `thinking`* → `finding_discovered`* → `agent_completed`
4. Return `AgentResult` with findings
5. Register in `CoordinatorAgent.__init__(specialists=[...])` when instantiating

### Add a New Workflow Step

1. Add a node function to `CoordinatorAgent._build_graph()`
2. Define state inputs/outputs as dict returns
3. Add edges to the graph
4. Emit events as needed via `event_callback()`

### Modify Consolidation Logic

Edit `CoordinatorAgent._consolidate_findings()` to change deduplication strategy:
- Current: Keep highest severity for same (category, line)
- Alternative: Merge descriptions, keep all, weighted scoring, etc.
