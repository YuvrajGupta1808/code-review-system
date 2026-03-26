# B10: Coordinator Agent Implementation

## Overview
The Coordinator agent orchestrates the code review process by:
1. Analyzing code structure
2. Creating an execution plan
3. Delegating to specialist agents
4. Consolidating findings
5. Producing a final report

## Architecture

### Constructor
```python
CoordinatorAgent(specialists: list[BaseAgent] | None = None)
```
- Accepts injected specialist agents (Security, Bug, etc.)
- Allows for easy composition and testing
- No hardcoded agent types

### Main Flow: `analyze(code, context, event_callback)`

#### 1. **agent_started** → Parse Code
- Lightweight AST parsing to extract metadata:
  - Lines of code
  - Function/class counts
  - Import analysis

#### 2. **plan_created** → Generate Execution Plan
- Creates structured plan steps
- Parallel execution info for specialists
- Coordinator plan: parse → specialists (parallel) → consolidate

#### 3. **agent_delegated** → Run Specialists
- Emits delegation event for each specialist
- Runs all specialists concurrently with `asyncio.gather`
- Events from specialists flow directly to event bus (pass-through callback)
- Errors in one specialist don't halt others

#### 4. **findings_consolidated** → Merge & Deduplicate
Conflict resolution by (category, line):
- Keep finding with **highest severity** when duplicates found
- Count resolved conflicts
- Generate severity distribution (critical/high/medium/low/info)

#### 5. **final_report** → Summary
- Executive summary with finding count
- List of critical findings
- Fix counts (from context)
- Ready for UI display

#### 6. **agent_completed** → Clean Up
- Total duration
- Final finding count

## Event Sequence
```
agent_started
  └─ plan_created
  └─ agent_delegated (for each specialist)
  └─ agent_delegated (for each specialist)
  ┌─ [specialist events stream directly]
  └─ findings_consolidated
  └─ final_report
  └─ agent_completed
```

## Key Design Decisions

### 1. **Dependency Injection**
Specialists are injected via constructor, not hardcoded. This allows:
- Easy testing with mock agents
- Adding new specialists without changing Coordinator
- Flexible composition for different deployment scenarios

### 2. **Event Pass-Through**
Specialist events flow directly to the shared event bus via the callback:
- No re-wrapping or duplicate events
- Preserves agent context from specialists
- UI sees raw event stream without coordinator interference

### 3. **Conflict Resolution Strategy**
Deduplicates by (category, line) keeping **highest severity**:
- Prevents alert fatigue from duplicate findings
- Relies on specification order (critical > high > medium > low > info)
- Counts resolved conflicts for metrics

### 4. **Graceful Degradation**
- One specialist error doesn't halt review
- Error caught, emitted as `agent_error`, others continue
- Final result includes partial findings from working specialists

### 5. **No LLM Required for Planning**
Code structure analysis uses stdlib `ast` module only:
- Fast plan generation (no network calls)
- Deterministic (no model randomness)
- Can run without credentials

## Integration Points

### With Event Bus
```python
async def bus_callback(event):
    await bus.publish(event)

result = await coordinator.analyze(code, context, bus_callback)
```

### With Specialist Agents
```python
coordinator = CoordinatorAgent(specialists=[
    SecurityAgent(llm_client),
    BugAgent(llm_client),
])
result = await coordinator.analyze(code, context, event_callback)
```

### With FastAPI Endpoint
Coordinator would be invoked by a WebSocket or HTTP endpoint that:
1. Accepts code input from UI
2. Creates event_callback connected to event bus
3. Runs `coordinator.analyze()` and awaits completion
4. Events stream to connected clients in real-time

## Testing Notes

The implementation has been validated with:
- ✓ Instantiation without specialists
- ✓ Concurrent delegation to mock specialists
- ✓ Finding consolidation and conflict resolution
- ✓ Event sequence correctness
- ✓ Event bus integration

Run tests:
```bash
# Quick import test
python -c "from backend.agents.coordinator import CoordinatorAgent; print('OK')"
```

## Files Modified/Created

- **Created**: `backend/agents/coordinator.py` (11 KB)
- **Updated**: `backend/agents/__init__.py` (exports CoordinatorAgent)

## Next Steps

To complete the agent architecture (B6-B12), you will need:
1. **B6**: MiniMax LLM client (loads env vars, streaming)
2. **B8**: SecurityAgent (uses LLM client, emits findings)
3. **B9**: BugAgent (uses LLM client, emits findings)
4. **B11**: Review session wiring (FastAPI endpoint that invokes coordinator)
5. **B12**: Fix lifecycle (enhance agents to emit fix_proposed/fix_verified)

The Coordinator skeleton is ready to accept real agents once they're implemented.
