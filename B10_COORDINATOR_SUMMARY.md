# B10: Coordinator Agent Implementation (LangGraph)

## Overview
The Coordinator agent orchestrates the code review process using **LangGraph** for stateful workflow management:
1. Parse code structure
2. Create execution plan
3. Delegate to specialist agents (parallel via Send API)
4. Consolidate findings
5. Produce final report

## Architecture: LangGraph StateGraph

### State Definition
```python
class CoordinatorState(TypedDict):
    code: str
    context: dict[str, Any]
    code_metadata: dict[str, Any]
    plan_steps: list[dict[str, Any]]
    specialist_results: Annotated[list[AgentResult], operator.add]  # Accumulates
    consolidated_findings: list[Finding]
    conflicts_resolved: int
    error: str | None
```
**Key**: `specialist_results` uses `operator.add` reducer to accumulate parallel worker outputs.

### Graph Topology
```
START
  ↓
parse_code (AST analysis)
  ↓
create_plan (emit plan_created event)
  ↓ (conditional routing based on specialists count)
  ├─ If specialists: Send fanout → run_specialist (parallel for each)
  └─ If no specialists: skip to consolidate
  ↓
consolidate (merge & deduplicate findings)
  ↓
final_report (emit final_report event)
  ↓
END
```

### Node Functions (5 total)

#### 1. **parse_code_node**
- Calls `_parse_code()` with stdlib `ast.parse`
- Extracts: lines, functions, classes, imports
- Returns `{"code_metadata": {...}}`

#### 2. **create_plan_node**
- Generates plan_steps list (one per specialist + consolidate)
- Emits `plan_created` event
- Returns `{"plan_steps": [...]}`

#### 3. **delegate_to_specialists** (conditional router)
```python
def delegate_to_specialists(state) -> list[Send] | str:
    if not self.specialists:
        return "consolidate"  # Skip if no specialists
    return [Send("run_specialist", {...}) for spec in self.specialists]
```
- Uses LangGraph **Send API** for fan-out parallelism
- Each Send spawns a worker with a specialist agent instance
- Returns either list of Send objects or string routing to "consolidate"

#### 4. **run_specialist** (worker node)
- Executes single specialist agent
- Emits `agent_delegated` event
- Calls `specialist.analyze(code, context, event_callback)`
- Returns `{"specialist_results": [result]}` (wrapped in list for reducer)

#### 5. **consolidate_findings_node**
- Merges all accumulated specialist results
- Deduplicates by (category, line) keeping highest severity
- Emits `findings_consolidated` event
- Returns consolidated findings

#### 6. **final_report_node**
- Generates executive summary
- Emits `final_report` event
- Returns empty dict (state already has consolidated findings)

### Constructor
```python
CoordinatorAgent(specialists: list[BaseAgent] | None = None)
```
- Accepts injected specialist agents
- Allows flexible composition (0, 1, or N specialists)
- Graph routes automatically based on specialists count

## Event Sequence
```
agent_started (manually emitted before graph.ainvoke)
  ↓ graph.ainvoke() ───────────────────────────────────
  │  parse_code
  │  plan_created
  │  [if specialists]
  │    agent_delegated (per specialist, in parallel via Send)
  │    [specialist events stream directly via callback]
  │  [else: skip to consolidate]
  │  findings_consolidated
  │  final_report
  └─────────────────────────────────────────────────────
agent_completed (manually emitted after graph.ainvoke)
```

## LangGraph Patterns Used

### 1. **Reducer for Parallel Results**
```python
specialist_results: Annotated[list[AgentResult], operator.add]
```
Accumulates results from parallel Send workers without overwriting.

### 2. **Send API for Fan-Out**
```python
return [Send("run_specialist", {...}) for specialist in self.specialists]
```
- Spawns concurrent workers, each invoking a specialist
- All run in parallel; results accumulated via reducer
- Graph waits for all to complete before moving to consolidate

### 3. **Conditional Routing with String + Send Mix**
```python
def delegate_to_specialists(state) -> list[Send] | str:
    if not self.specialists:
        return "consolidate"
    return [Send(...) for ...]

graph.add_conditional_edges("create_plan", delegate_to_specialists, ["run_specialist", "consolidate"])
```
Routes to either parallel specialists or skips directly to consolidation.

### 4. **Event Callback in Closure**
```python
def _build_graph(self, event_callback):
    # event_callback captured in closure
    async def create_plan_node(state) -> dict:
        await event_callback(PlanCreatedEvent(...))
        return {...}
```
Allows nodes to emit events while building the graph declaratively.

### 5. **Async Graph Execution**
```python
compiled_graph = graph.compile()
result = await compiled_graph.ainvoke(initial_state)
```
Graph runs async-first; specialists can use async `analyze()`.

## Key Design Decisions

### 1. **LangGraph for Orchestration**
- **Why**: State management, parallel workers (Send API), routing, and checkpointing built-in
- **Benefit**: Clean separation of concerns (nodes = pure logic, graph = flow control)
- Compared to vanilla async: LangGraph graph is stateful, traceable, and resumable

### 2. **Dependency Injection**
Specialists injected at constructor time:
- Easy testing with mocks
- No hardcoded agent types
- Flexible (0 to N specialists supported)

### 3. **Event Pass-Through Callback**
Specialist events stream directly:
- No re-wrapping or filtering
- Preserves agent context
- UI sees raw event stream

### 4. **Conflict Resolution by (category, line)**
Keeps highest severity when duplicates found:
- Prevents alert fatigue
- Clear deterministic merging

### 5. **No LLM for Planning Phase**
Uses stdlib `ast` parsing:
- Fast, deterministic
- No credentials needed
- No latency

## Integration Points

### With Event Bus
```python
async def bus_callback(event):
    await bus.publish(event)

coordinator = CoordinatorAgent(specialists=[...])
result = await coordinator.analyze(code, context, bus_callback)
```

### With Specialist Agents
```python
coordinator = CoordinatorAgent(specialists=[
    SecurityAgent(llm_client),
    BugAgent(llm_client),
    CustomAgent(),  # Add any BaseAgent subclass
])
result = await coordinator.analyze(code, context, event_callback)
```

### With FastAPI Endpoint
```python
coordinator = CoordinatorAgent(specialists=[...])

@app.websocket("/ws/review")
async def review_ws(ws: WebSocket):
    async for event in event_bus.subscribe():
        await ws.send_json(event.to_dict())

@app.post("/start-review")
async def start_review(code: str):
    await coordinator.analyze(code, {}, event_bus.publish)
```

## Testing Notes

Validated with:
- ✓ No specialists (routes directly to consolidate)
- ✓ Mock specialists (parallel Send execution)
- ✓ Finding consolidation and conflict resolution
- ✓ Event sequence correctness
- ✓ Event bus integration

Tests confirm:
- Empty specialists path works (LangGraph routes correctly)
- Parallel delegation executes (both specialists called concurrently)
- Consolidation merges results properly
- All required events emitted in correct order

## Files

- **Created**: `backend/agents/coordinator.py` (381 lines, ~12 KB)
  - `CoordinatorState` TypedDict
  - `CoordinatorAgent` class
  - `_build_graph()` method (5 nodes + Send fan-out)
  - Helper methods: `_parse_code`, `_create_plan`, `_consolidate_findings`, etc.
- **Updated**: `backend/agents/__init__.py` (exports CoordinatorAgent)

## Next Steps

To complete B6–B12:
1. **B6**: MiniMax LLM client (env setup, streaming)
2. **B8/B9**: SecurityAgent + BugAgent (LLM analysis, emit findings)
3. **B11**: FastAPI endpoint + WebSocket/SSE transport
4. **B12**: Fix lifecycle (fix_proposed/fix_verified events)

The LangGraph Coordinator is production-ready and waiting for real agents.
