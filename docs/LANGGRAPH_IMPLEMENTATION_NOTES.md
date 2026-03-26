# LangGraph Implementation Notes — B10 Coordinator

## Overview
The B10 Coordinator agent uses **LangGraph 1.0** for state management and workflow orchestration.

## Graph Architecture

### StateGraph
```python
class CoordinatorState(TypedDict):
    code: str
    context: dict[str, Any]
    code_metadata: dict[str, Any]
    plan_steps: list[dict[str, Any]]
    specialist_results: Annotated[list[AgentResult], operator.add]  # Key: reducer
    consolidated_findings: list[Finding]
    conflicts_resolved: int
    error: str | None
```

The **reducer** (`operator.add`) on `specialist_results` is critical:
- When parallel workers (Send nodes) return `{"specialist_results": [result]}`, the list is **appended** not overwritten
- Without reducer: last worker result would overwrite all others
- With reducer: all results accumulated in order

### Execution Flow

```
START
  ↓
parse_code (async, emits nothing)
  ↓ return {"code_metadata": {...}}
  ↓
create_plan (async, emits plan_created)
  ↓ return {"plan_steps": [...]}
  ↓
delegate_to_specialists (conditional router)
  ├─ If specialists empty: return "consolidate" → skip directly
  └─ If specialists present: return [Send(...), Send(...), ...] → fan-out
  ↓ (Send spawns parallel workers)
run_specialist (async, worker node, emits agent_delegated)
  ↓ return {"specialist_results": [result]}  ← reducer accumulates
  ↓
consolidate (async, emits findings_consolidated)
  ↓ return {"consolidated_findings": [...], "conflicts_resolved": N}
  ↓
final_report (async, emits final_report)
  ↓ return {}
  ↓
END
```

## Key LangGraph Patterns

### 1. Reducer for Accumulation
```python
specialist_results: Annotated[list[AgentResult], operator.add]
```
- Each Send worker returns `{"specialist_results": [one_result]}`
- Reducer combines: `[] + [result1] = [result1]`, then `[result1] + [result2] = [result1, result2]`, etc.

### 2. Send API for Parallelism
```python
def delegate_to_specialists(state: CoordinatorState) -> list[Send] | str:
    if not self.specialists:
        return "consolidate"
    return [
        Send("run_specialist", {
            "specialist": specialist,
            "code": state["code"],
            "context": state["context"],
        })
        for specialist in self.specialists
    ]
```
- Returns list of `Send` objects to spawn workers
- LangGraph automatically runs all Send workers in parallel
- All results accumulated via reducer before moving to `consolidate`

### 3. Conditional Edges (Mixed Routing)
```python
graph.add_conditional_edges(
    "create_plan",
    delegate_to_specialists,
    ["run_specialist", "consolidate"]  # Declare both possible routes
)
```
- Router function can return either:
  - List of `Send` objects → routes to the target node of those Send calls
  - String node name → routes directly to that node
- Allows "skip specialists if none configured" pattern

### 4. Closure-Based Event Callback
```python
def _build_graph(self, event_callback: Callable) -> StateGraph:
    # event_callback is captured in closure
    async def create_plan_node(state: CoordinatorState) -> dict:
        await event_callback(PlanCreatedEvent(...))
        return {...}

    graph = StateGraph(CoordinatorState)
    graph.add_node("create_plan", create_plan_node)
```
- Clean way to pass event emitter to nodes
- Nodes emit events as they run
- No need to pass callback through state

### 5. Async Execution
```python
graph = StateGraph(CoordinatorState).add_node(...).compile()
result = await compiled_graph.ainvoke(initial_state)
```
- Use `ainvoke()` for async graph (all nodes are async)
- Use `invoke()` for sync (mixed or all sync nodes)
- Initial state must include all TypedDict fields

## Bug Fix: Empty Specialists

**Problem**: When `specialists=[]`, `delegate_to_specialists` returned `[]` (empty list of Send objects).
LangGraph would have no path forward and the graph would stall.

**Solution**: Return string route name when no specialists:
```python
def delegate_to_specialists(state) -> list[Send] | str:
    if not self.specialists:
        return "consolidate"  # ← Direct string route
    return [Send(...) for ...]  # ← Or Send list for fan-out
```

Declare both routes in `add_conditional_edges`:
```python
graph.add_conditional_edges("create_plan", delegate_to_specialists, ["run_specialist", "consolidate"])
#                                                                     ^^^^^^^^^^^^^   ^^^^^^^^^^^
#                                                                     Send target     String route
```

## Integration Checklist

- [x] StateGraph defined with state schema
- [x] Reducer for parallel result accumulation
- [x] 5 node functions (parse, plan, run_specialist, consolidate, final_report)
- [x] Send API for fan-out to specialists
- [x] Conditional routing (Send or string route)
- [x] Event callback in closure
- [x] Graph compilation
- [x] Async execution with ainvoke()
- [x] Empty specialists edge case handled

## Testing

All tests pass:
- ✓ Empty specialists routes correctly to consolidate
- ✓ Multiple specialists run in parallel
- ✓ Finding consolidation merges results
- ✓ Event sequence correct
- ✓ Graph compilation succeeds

## Notes for Future Development

### When Adding More Nodes
- Update `CoordinatorState` TypedDict with new fields
- Add reducer if new field accumulates (e.g., list of findings from multiple sources)
- Add `graph.add_node(name, async_func)` call
- Add edges or conditional edges as needed

### When Adding Reducers
- Use `Annotated[list, operator.add]` for appending lists
- Use custom reducer function for complex merge logic:
  ```python
  def merge_findings(existing, new):
      # Custom merge logic
      return merged

  findings: Annotated[list[Finding], merge_findings]
  ```

### Streaming Events
LangGraph supports streaming state changes:
```python
async for event in graph.astream(initial_state):
    print(event)  # (node_name, state_update)
```
Can be used for real-time event emission (alternative to callback approach).

## References

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [StateGraph API](https://api.python.langchain.com/en/latest/langgraph/langgraph.graph.state.StateGraph.html)
- [Send Type](https://api.python.langchain.com/en/latest/langgraph/langgraph.types.Send.html)
