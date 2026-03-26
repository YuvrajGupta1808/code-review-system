# Frontend Integration Guide

## Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
Visit `http://localhost:5173` - UI will load with mock events for demo.

### 3. Connect to Backend (Optional)

To connect to a real backend instead of mock events:

**Edit `frontend/src/App.tsx`:**
```typescript
// Change this line:
const useMock = import.meta.env.DEV

// To:
const useMock = false  // or remove && use real backend
```

Make sure backend is running:
```bash
cd backend
python -m uvicorn backend.main:create_app --reload --host 0.0.0.0 --port 8000
```

## Event Stream Contract

### WebSocket Endpoint
```
ws://localhost:8000/ws/review
```

### Event Message Format
All messages must be JSON with this structure:

```typescript
interface StreamEvent {
  event_type: string
  agent_id: 'coordinator' | 'security_agent' | 'bug_agent'
  timestamp: string  // ISO 8601
  event_id: string   // UUID
  data: Record<string, any>
}
```

### Supported Event Types & Payloads

#### 1. Agent Lifecycle

**agent_started**
```json
{
  "event_type": "agent_started",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T10:30:00Z",
  "event_id": "evt_123",
  "data": {
    "message": "Starting security analysis"
  }
}
```

**agent_completed**
```json
{
  "event_type": "agent_completed",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T10:30:05Z",
  "event_id": "evt_124",
  "data": {}
}
```

**agent_error**
```json
{
  "event_type": "agent_error",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T10:30:06Z",
  "event_id": "evt_125",
  "data": {
    "error": "Analysis failed: timeout",
    "traceback": "..."
  }
}
```

#### 2. Thinking/Reasoning

**thinking**
```json
{
  "event_type": "thinking",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T10:30:01Z",
  "event_id": "evt_126",
  "data": {
    "content": "Analyzing the database query on line 45..."
  }
}
```

**Note**: Emit multiple `thinking` events as the agent reasons. Each event's `data.content` is a thought segment. UI auto-scrolls and shows cursor on latest.

#### 3. Tool Calls

**tool_call_start**
```json
{
  "event_type": "tool_call_start",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T10:30:02Z",
  "event_id": "evt_127",
  "data": {
    "tool_name": "code_scanner",
    "input": {
      "file": "main.py",
      "patterns": ["sql_injection", "xss"]
    }
  }
}
```

**tool_call_result**
```json
{
  "event_type": "tool_call_result",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T10:30:02Z",
  "event_id": "evt_128",
  "data": {
    "tool_name": "code_scanner",
    "output": {
      "issues": 2,
      "vulnerabilities": ["sql_injection", "hardcoded_secret"]
    },
    "duration_ms": 150
  }
}
```

#### 4. Findings

**finding_discovered**
```json
{
  "event_type": "finding_discovered",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T10:30:03Z",
  "event_id": "evt_129",
  "data": {
    "finding_id": "sqli_001",
    "severity": "critical",
    "category": "sql_injection",
    "line": 45,
    "description": "SQL injection vulnerability",
    "details": "User input concatenated into query without parameterization"
  }
}
```

**Severity values**: `critical`, `high`, `medium`, `low`, `info`

**Categories**: `sql_injection`, `xss`, `hardcoded_secret`, `null_reference`, `logic_error`, `race_condition`, `type_mismatch`, `resource_leak`, `auth_bypass`, `error_handling`

#### 5. Fixes

**fix_proposed**
```json
{
  "event_type": "fix_proposed",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T10:30:04Z",
  "event_id": "evt_130",
  "data": {
    "finding_id": "sqli_001",
    "proposed_fix": "query = 'SELECT * FROM users WHERE id = ?'\ncursor.execute(query, (user_id,))",
    "explanation": "Use parameterized queries to prevent SQL injection",
    "confidence": 0.95
  }
}
```

**fix_verified**
```json
{
  "event_type": "fix_verified",
  "agent_id": "security_agent",
  "timestamp": "2026-03-25T10:30:05Z",
  "event_id": "evt_131",
  "data": {
    "finding_id": "sqli_001",
    "verification_passed": true,
    "test_output": "All tests passed",
    "duration_ms": 234
  }
}
```

#### 6. Coordinator Workflow

**plan_created**
```json
{
  "event_type": "plan_created",
  "agent_id": "coordinator",
  "timestamp": "2026-03-25T10:30:00Z",
  "event_id": "evt_132",
  "data": {
    "steps": [
      "Parse code structure",
      "Security analysis",
      "Bug detection",
      "Consolidate findings",
      "Generate fixes",
      "Final report"
    ]
  }
}
```

**agent_delegated**
```json
{
  "event_type": "agent_delegated",
  "agent_id": "coordinator",
  "timestamp": "2026-03-25T10:30:00Z",
  "event_id": "evt_133",
  "data": {
    "agent_name": "Security Agent",
    "task": "security analysis"
  }
}
```

**findings_consolidated**
```json
{
  "event_type": "findings_consolidated",
  "agent_id": "coordinator",
  "timestamp": "2026-03-25T10:30:10Z",
  "event_id": "evt_134",
  "data": {
    "total_findings": 5,
    "critical": 2,
    "high": 1,
    "medium": 2
  }
}
```

**final_report**
```json
{
  "event_type": "final_report",
  "agent_id": "coordinator",
  "timestamp": "2026-03-25T10:30:15Z",
  "event_id": "evt_135",
  "data": {
    "total_findings": 5,
    "critical": 2,
    "high": 1,
    "medium": 2,
    "fixes_proposed": 3,
    "fixes_verified": 2
  }
}
```

## Backend Integration Points

### 1. FastAPI WebSocket Endpoint

Your backend should expose a WebSocket endpoint that sends `StreamEvent` JSON:

```python
from fastapi import FastAPI, WebSocket
from backend.models import StreamEvent

app = FastAPI()

@app.websocket("/ws/review")
async def review_websocket(websocket: WebSocket):
    await websocket.accept()

    # Subscribe to event bus
    async for event in event_bus.subscribe():
        await websocket.send_json(event.model_dump())
```

### 2. CORS Configuration

Ensure CORS is configured to allow frontend origin:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Event Emission

When agents emit events, they should flow through your event bus:

```python
async def analyze(code: str, event_callback):
    # Start event
    event_callback(AgentStartedEvent(agent_id="security_agent"))

    # Thinking events (streaming)
    for thought in stream_thoughts(code):
        event_callback(ThinkingEvent(
            agent_id="security_agent",
            data={"content": thought}
        ))

    # Finding events
    for finding in findings:
        event_callback(FindingDiscoveredEvent(
            agent_id="security_agent",
            data={
                "finding_id": finding.id,
                "severity": finding.severity,
                "category": finding.category,
                "line": finding.line,
                "description": finding.description,
            }
        ))

    # Completion
    event_callback(AgentCompletedEvent(agent_id="security_agent"))
```

## Frontend State Management

### Store Structure

The Zustand store tracks:

```typescript
interface ReviewStore {
  // Agent tracking
  agents: Map<AgentType, AgentState>
  updateAgentStatus: (agentId, status) => void

  // Events
  events: StreamEvent[]
  addEvent: (event) => void

  // Findings
  findings: Finding[]
  addFinding: (finding) => void
  updateFinding: (id, partial) => void

  // Tool calls
  toolCalls: ToolCall[]
  addToolCall: (toolCall) => void

  // Thoughts
  thoughts: ThoughtStreamEntry[]
  addThought: (thought) => void

  // Plan
  plan: PlanStep[]
  setPlan: (plan) => void
  updatePlanStep: (stepId, status) => void

  // Connection
  isConnected: boolean
  setConnected: (connected) => void
}
```

### How Events Update State

1. **WebSocket receives JSON**
2. **useWebSocket hook parses event**
3. **Hook dispatches to store based on event type**:
   - `agent_started`/`thinking` → `updateAgentStatus('thinking')`
   - `thinking` → `addThought()`
   - `tool_call_*` → `addToolCall()`
   - `finding_discovered` → `addFinding()`
   - `plan_created` → `setPlan()`
   - `agent_delegated` → `updatePlanStep()`

4. **Components subscribe to store and re-render**

### Adding Custom Logic

To add logic when an event arrives, modify `useWebSocket.ts`:

```typescript
if (streamEvent.event_type === 'your_event') {
  // Custom handling
  store.doSomething(streamEvent.data)
}
```

## Development Workflow

### Step 1: Backend Emits Events
```python
# backend/agents/security_agent.py
async def analyze(code, context, event_callback):
    await event_callback(AgentStartedEvent(...))
    # ... analysis ...
    await event_callback(ThinkingEvent(...))
    # ... more analysis ...
    await event_callback(AgentCompletedEvent(...))
```

### Step 2: Frontend Receives via WebSocket
Browser DevTools → Network → WS → Messages tab shows events

### Step 3: Frontend Updates UI
Store → Components → Visual update (animated)

### Step 4: Verify in Browser
- Agent status changes color/animation
- Thoughts appear and auto-scroll
- Findings expand with details
- Plan progresses

## Testing

### Mock Events (Development)
UI loads with 8500ms of simulated events:
```bash
npm run dev  # Mock events enabled by default
```

### Real Backend
Connect to actual backend:

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn backend.main:create_app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
# Edit App.tsx: const useMock = false
```

### Browser DevTools
1. **WebSocket Inspector**: View all messages in Network tab
2. **React DevTools**: Inspect component props/state
3. **Console**: Check for errors/warnings

## Troubleshooting

### WebSocket Connect Fails
**Problem**: `WebSocket connection failed`

**Solutions**:
1. Check backend running: `curl http://localhost:8000/health`
2. Check CORS in backend allows `http://localhost:5173`
3. Check firewall/network

### Events Not Updating UI
**Problem**: Events arrive but components don't update

**Solutions**:
1. Verify `useWebSocket()` called in App component
2. Check store subscription: `const { agents } = useStore()`
3. Look for errors in console
4. Check event JSON structure matches schema

### Performance Issues
**Problem**: UI lag, animations stutter

**Solutions**:
1. Check event frequency (< 100 events/sec)
2. Reduce visible history (edit store max sizes)
3. Check for console errors
4. Profile with Chrome DevTools → Performance

### Mock Events Not Running
**Problem**: No events appearing, UI stays empty

**Solutions**:
1. Check `useMock = true` in App.tsx
2. Check console for JavaScript errors
3. Open DevTools → Console → check for exceptions
4. Clear browser cache and reload

## Production Deployment

### Build
```bash
cd frontend
npm run build
# Output: dist/ directory with optimized files
```

### Serve
```bash
npm run preview  # Local preview
# Or deploy dist/ to CDN/static server
```

### Environment Variables
Create `.env.production`:
```
VITE_API_URL=https://api.example.com
```

Use in frontend:
```typescript
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

## Performance Optimization Checklist

- [ ] Bundle size < 200KB gzip
- [ ] Lighthouse score > 90
- [ ] First Contentful Paint < 1.5s
- [ ] Theme toggle < 100ms
- [ ] Event processing < 5ms per event
- [ ] 60 FPS animations maintained
- [ ] No console errors/warnings
- [ ] Mobile responsive tested
- [ ] Accessibility audit passed
- [ ] Dark mode tested thoroughly

---

**Integration Guide Version**: 1.0
**Last Updated**: 2026-03-25
**Backend Version Required**: ≥ 0.1.0
