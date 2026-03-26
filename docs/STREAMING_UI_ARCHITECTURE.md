# Streaming UI Architecture

## System Overview

The Streaming UI is a real-time visualization system that displays agent activities during code review analysis. It receives events from the backend through a WebSocket connection and renders them with smooth animations.

## Data Flow

```
Backend Events
     │
     ▼
WebSocket (JSON)
     │
     ▼
useWebSocket Hook
├─ Parse JSON
├─ Route to handlers
└─ Dispatch to store
     │
     ▼
Zustand Store
├─ agents map
├─ findings array
├─ thoughts array
├─ toolCalls array
├─ plan array
└─ UI state
     │
     ▼
React Components
├─ Subscribe to store
├─ Compute derived state
└─ Render with animations
```

## Component Hierarchy

```
App
├─ Header
│  ├─ Connection status
│  ├─ Theme toggle
│  └─ Logo
│
├─ Main (Grid Layout)
│  │
│  ├─ Row 1: 2-column grid
│  │  ├─ AgentStatusPanel
│  │  │  └─ 3 x AgentStatusCard
│  │  │
│  │  └─ ExecutionPlanPanel
│  │     └─ 6 x PlanStepItem
│  │
│  ├─ Row 2: 2-column grid
│  │  ├─ ThoughtStreamPanel
│  │  │  └─ Multiple ThoughtEntry
│  │  │
│  │  └─ FindingsFeed
│  │     ├─ SummaryGrid (4 severity counts)
│  │     └─ Multiple FindingItem (expandable)
│  │
│  └─ Row 3: Full-width
│     └─ ToolActivityPanel
│        └─ Multiple ToolCallEntry
│
└─ Footer
```

## State Management Deep Dive

### Store Structure

```typescript
interface ReviewStore {
  // Agent State
  agents: Map<AgentType, {
    id: AgentType
    name: string
    status: AgentStatus      // idle|thinking|tool_calling|completed|error
    startTime?: number       // Unix timestamp
    endTime?: number         // Unix timestamp
  }>

  // Event Log
  events: StreamEvent[]      // Last 1000 events

  // Analysis Results
  findings: Finding[]        // Discovered issues
  toolCalls: ToolCall[]      // Tool invocations (last 500)
  thoughts: ThoughtEntry[]   // Agent reasoning (last 200)
  plan: PlanStep[]           // Execution plan steps

  // UI State
  theme: 'light' | 'dark'
  isConnected: boolean
  selectedFindingId?: string
  currentReviewId?: string
}
```

### Store Selectors (Component Usage)

```typescript
// In components:
const { agents, findings, theme } = useStore()  // Pull specific slices
const { updateAgentStatus, addFinding } = useStore()  // Pull actions
```

### State Updates Flow

```
Event arrives via WebSocket
        │
        ▼
useWebSocket.onmessage()
        │
        ├─ Parse JSON
        ├─ Validate structure
        │
        ▼
Route by event_type:
        │
        ├─ agent_started → updateAgentStatus(id, 'thinking')
        ├─ agent_completed → updateAgentStatus(id, 'completed')
        ├─ thinking → addThought() + updateAgentStatus
        ├─ tool_call_start → addToolCall()
        ├─ tool_call_result → addToolCall() with output
        ├─ finding_discovered → addFinding()
        ├─ fix_proposed → addFinding() with proposedFix
        ├─ fix_verified → updateFinding(id, { fixVerified: true })
        ├─ plan_created → setPlan()
        ├─ agent_delegated → updatePlanStep()
        │
        ▼
Store updates (immutable)
        │
        ▼
Components re-render (via hooks)
        │
        ▼
UI updates with animations
```

## Hook System

### useWebSocket Hook

**Purpose**: Manage WebSocket lifecycle and event routing

**Responsibilities**:
1. Create WebSocket connection to backend
2. Parse incoming JSON events
3. Dispatch events to store
4. Handle connection/disconnection
5. Implement auto-reconnect with exponential backoff

**Usage**:
```typescript
const { isConnected, send } = useWebSocket(reviewId)
```

**Connection States**:
- **Initial**: Not connected
- **Connecting**: WebSocket created, waiting for accept
- **Connected**: Can send/receive
- **Reconnecting**: Lost connection, attempting to restore
- **Failed**: Max reconnection attempts exceeded

**Reconnection Logic**:
```
Attempt 1: 1s delay
Attempt 2: 2s delay
Attempt 3: 4s delay
Attempt 4: 8s delay
Attempt 5: 10s delay
↓
Give up (max 5 attempts)
```

### useMockEvents Hook

**Purpose**: Generate realistic mock events for development/demo

**Responsibilities**:
1. Schedule event emissions over 8.5 seconds
2. Simulate complete review workflow
3. Include all event types (agents, thoughts, tools, findings)

**Sequence**:
```
0.5s: Coordinator starts
1.5s: Plan created
2.0s: Security agent starts
2.2-3.5s: Streaming thoughts (8 total, spaced 300ms apart)
4.5s: Tool call starts
5.0s: Tool call results
5.2-7.0s: 5 findings discovered (spaced 400ms)
7.0s: Fix proposed
7.2s: Bug agent starts
8.5s: All agents complete, final report
```

## Component Details

### AgentStatusPanel

**Data Source**: `agents` map from store

**Update Trigger**: `updateAgentStatus` action

**Key Features**:
- 3-agent list (one per specialist)
- Color-coded badges (idle=gray, thinking=blue, etc.)
- Pulse animation on active agents
- Smooth transitions between states

**Re-render**: On agent status change

### ThoughtStreamPanel

**Data Source**: `thoughts` array (last 5 entries)

**Update Trigger**: `addThought` action

**Key Features**:
- Groups thoughts by agent
- Auto-scrolls to latest
- Cursor blink on current thought
- Colored by agent

**Re-render**: On new thought added

### ToolActivityPanel

**Data Source**: `toolCalls` array (last 8 entries)

**Update Trigger**: `addToolCall` action

**Key Features**:
- Shows inputs and outputs as JSON
- Displays execution duration
- Syntax-highlighted code blocks
- Auto-scrolls to latest

**Re-render**: On new tool call added

### FindingsFeed

**Data Source**: `findings` array (all, sorted by severity)

**Update Trigger**: `addFinding` action

**Key Features**:
- Sortable by severity
- Expandable cards with details
- Severity summary grid (4 counts)
- Shows proposed fixes
- Indicates fix verification status

**Re-render**: On new finding or update

### ExecutionPlanPanel

**Data Source**: `plan` array

**Update Trigger**: `setPlan` and `updatePlanStep` actions

**Key Features**:
- Shows 6 workflow steps
- Status indicators (pending, in_progress, completed)
- Animated progress
- Linear workflow display

**Re-render**: On plan change

## Event Type Handling

### Agent Lifecycle Events

```
agent_started
├─ Action: updateAgentStatus(agent_id, 'thinking')
└─ UI: Agent card color changes, badge appears

agent_completed
├─ Action: updateAgentStatus(agent_id, 'completed')
├─ Action: updatePlanStep (if coordinator)
└─ UI: Agent card color green, badge disappears

agent_error
├─ Action: updateAgentStatus(agent_id, 'error')
└─ UI: Agent card red, error badge
```

### Analysis Events

```
thinking
├─ Action: addThought({ id, agent_id, content, timestamp })
├─ Action: updateAgentStatus(agent_id, 'thinking')
└─ UI: New thought appears in stream, auto-scrolls

tool_call_start
├─ Action: updateAgentStatus(agent_id, 'tool_calling')
└─ UI: Agent badge changes to tool_calling

tool_call_result
├─ Action: addToolCall({ tool_name, input, output, duration })
└─ UI: Tool entry appears in log, shows results

finding_discovered
├─ Action: addFinding({ id, severity, category, description, details })
└─ UI: Finding card appears, sorted by severity, animated slide-up

fix_proposed
├─ Action: addFinding with proposedFix field
└─ UI: Finding shows code fix in expandable detail

fix_verified
├─ Action: updateFinding(id, { fixVerified: true/false })
└─ UI: Finding shows green/red checkmark
```

### Coordinator Events

```
plan_created
├─ Action: setPlan([...steps])
└─ UI: Execution plan appears, all steps initially pending

agent_delegated
├─ Action: updatePlanStep(stepId, 'in_progress')
└─ UI: Step shows in-progress indicator (spinning loader)

findings_consolidated
├─ Informational (just logged)
└─ UI: No direct impact

final_report
├─ Informational (marks completion)
└─ UI: No direct impact
```

## Animation System

### Framer Motion Integration

Used for:
- Entrance animations (fade + slide)
- State transitions (color, opacity)
- Continuous animations (pulse, rotate)
- Layout animations (expand/collapse)

### Key Animation Patterns

**Entrance**:
```typescript
initial={{ opacity: 0, y: 10 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.3 }}
```

**Pulse**:
```typescript
animate={{ scale: [1, 1.1, 1] }}
transition={{ duration: 1, repeat: Infinity }}
```

**Rotate**:
```typescript
animate={{ rotate: 360 }}
transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
```

**Height Expand**:
```typescript
initial={{ opacity: 0, height: 0 }}
animate={{ opacity: 1, height: 'auto' }}
exit={{ opacity: 0, height: 0 }}
```

## Styling Architecture

### Tailwind CSS

**Configuration**:
- Dark mode: Class-based (`darkMode: 'class'`)
- Custom colors: Semantic palette (critical, high, medium, low)
- Custom animations: Pulse, spin-slow, fade-in, slide-up
- Responsive breakpoints: sm (640px), md (768px), lg (1024px)

### Theme System

**Light Mode**:
- `bg-white`, `text-gray-900`
- `border-gray-200`

**Dark Mode**:
- `dark:bg-gray-900`, `dark:text-white`
- `dark:border-gray-800`

**Toggle**:
```typescript
toggleTheme() {
  const newTheme = theme === 'light' ? 'dark' : 'light'
  document.documentElement.classList.toggle('dark')
  // Update store
}
```

## Performance Optimization

### Memory Management

**Event History Limits**:
- Events: Last 1000
- Tool calls: Last 500
- Thoughts: Last 200

**Rationale**: Balance memory usage with showing sufficient history

**Implementation**:
```typescript
const events = [...state.events, event].slice(-1000)
```

### Re-render Optimization

**Component Subscriptions**:
- Components only subscribe to slices they use
- Zustand optimizes re-renders per slice

**Example**:
```typescript
const { findings } = useStore()  // Only re-renders on findings change
```

### Animation Performance

**GPU Acceleration**:
- Use `transform` and `opacity` (not `width`, `height`)
- Framer Motion handles this automatically

**Reduce Motion**:
- Respects `prefers-reduced-motion` media query
- Can disable animations system-wide

## Error Handling

### WebSocket Errors

```
Connection fails
    ↓
Log error to console
    ↓
Update isConnected to false
    ↓
Show "Disconnected" in header
    ↓
Attempt reconnect after delay
    ↓
Repeat up to 5 times
    ↓
Notify user if all attempts fail
```

### Event Parsing Errors

```
Invalid JSON received
    ↓
Log error with raw message
    ↓
Continue processing next event
    ↓
No UI impact (graceful degradation)
```

### Component Errors

```
Component throws error
    ↓
React Error Boundary catches (if added)
    ↓
Show error UI or fallback
    ↓
User can refresh to recover
```

## Extensibility Points

### Adding a New Panel

1. Create component: `src/components/NewPanel.tsx`
2. Add store accessor: `const { data } = useStore()`
3. Add to grid in `App.tsx`
4. Style with Tailwind

### Adding a New Event Type

1. Add to `EventType` enum in `types.ts`
2. Add handler in `useWebSocket.ts`
3. Add store action if needed
4. Update component to react to store change

### Adding a New Agent

1. Add to `AgentType` enum in `types.ts`
2. Initialize in store with `status: 'idle'`
3. Agent appears automatically in AgentStatusPanel
4. Update plan steps to reference new agent

## Testing Considerations

### Unit Testing

- Store actions (reducers)
- Utility functions (formatting)
- Type definitions

### Integration Testing

- Component rendering with mock store
- Event routing through hooks
- Animation timing

### E2E Testing

- WebSocket connection flow
- Complete review simulation
- UI updates in real-time

### Manual Testing

- Mock events (npm run dev)
- Real backend connection
- Theme toggle
- Responsive breakpoints
- Dark/light mode

## Deployment Checklist

- [ ] Build: `npm run build`
- [ ] No console errors/warnings
- [ ] All animations smooth (60 FPS)
- [ ] Responsive on mobile/tablet/desktop
- [ ] WebSocket connects to backend
- [ ] Events parse and display correctly
- [ ] Theme toggle works
- [ ] Dark mode looks good
- [ ] Lighthouse score > 90
- [ ] Bundle size < 200KB

## Monitoring & Debugging

### Browser DevTools

**Console**: Check for errors/warnings

**Network**:
- Monitor WebSocket messages
- Check JSON structure
- Verify event timing

**React DevTools**:
- Inspect component hierarchy
- Check props/state
- Monitor re-renders

**Performance**:
- Check frame rate
- Measure component render time
- Identify bottlenecks

### Logging

Add debugging:
```typescript
if (process.env.DEBUG) {
  console.log('Event received:', streamEvent)
}
```

---

**Architecture Version**: 1.0
**Last Updated**: 2026-03-25
**Maintainer**: Claude Code
