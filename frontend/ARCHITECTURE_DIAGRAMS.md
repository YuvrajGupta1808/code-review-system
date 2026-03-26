# Architecture Diagrams & Flow Charts

Visual representations of the IDE system architecture, component hierarchy, and data flow.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CODE REVIEW IDE SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐              ┌───────────────────────────┐ │
│  │  Home Screen    │              │    IDE Interface          │ │
│  │  (Landing Page) │              │   (Main Editor)           │ │
│  │                 │              │                           │ │
│  │ • Upload Button │─────────────▶│ ┌──────────────────────┐ │ │
│  │ • Write Button  │              │ │  IDE Toolbar         │ │ │
│  │ • Animations    │              │ │  (File, Controls)    │ │ │
│  └─────────────────┘              │ ├──────────────────────┤ │ │
│                                    │ │ CodeEditor │ Results │ │ │
│                                    │ │            │ Panel   │ │ │
│                                    │ │   (60%)    │ (30%)   │ │ │
│                                    │ ├────────────┤          │ │ │
│                                    │ │  Terminal  │          │ │ │
│                                    │ │  (40%)     │          │ │ │
│                                    │ └──────────────────────┘ │ │
│                                    └───────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────────┤
│  │              Zustand Store (State Management)                │
│  │  ┌────────────────────────────────────────────────────────┐ │
│  │  │ UI State:    uiMode, codeContent, fileName             │ │
│  │  │ Terminal:    terminalLogs[]                            │ │
│  │  │ Results:     findings[], toolCalls[], events[]         │ │
│  │  │ Agents:      agents Map, plan[]                        │ │
│  │  │ Connection:  isConnected, theme                        │ │
│  │  └────────────────────────────────────────────────────────┘ │
│  └──────────────────────────────────────────────────────────────┤
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

                             ▲  │
                             │  │ WebSocket
                             │  ▼

┌──────────────────────────────────────────────────────────────────┐
│                    Backend Server                                │
│  • Code Analysis API                                            │
│  • Agent Execution                                              │
│  • Real-time Event Streaming                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Hierarchy

```
App.tsx
│
├─ Route: uiMode === 'home'
│  └─ HomeScreen
│     ├─ Upload File Handler
│     └─ Write Code Handler
│
└─ Route: uiMode === 'editor'
   └─ IDEInterface
      │
      ├─ IDEToolbar
      │  ├─ File Name Display
      │  ├─ Connection Status
      │  ├─ Analyze Button
      │  ├─ Stop Button
      │  ├─ Reset Button
      │  ├─ Theme Toggle
      │  └─ Home Button
      │
      └─ Main Content Area (flex row)
         │
         ├─ Left Column (flex-1, vertical split)
         │  └─ SplitPane (vertical, 60/40)
         │     │
         │     ├─ CodeEditor (60%)
         │     │  ├─ Line Numbers Column
         │     │  └─ Textarea with Syntax Highlighting
         │     │
         │     └─ Terminal (40%)
         │        ├─ Header with Window Controls
         │        ├─ Log Output Area
         │        └─ Clear Button
         │
         └─ Right Column (w-96, fixed)
            └─ ResultsPanel
               ├─ Header
               ├─ Tab Navigation
               │  ├─ Findings Tab
               │  ├─ Logs Tab
               │  └─ Events Tab
               │
               └─ Content Area (Tab-specific)
                  ├─ FindingsTab
                  │  └─ Finding Cards (expandable)
                  │     ├─ Severity Icon
                  │     ├─ Category & Severity
                  │     ├─ Description
                  │     ├─ Details (expanded)
                  │     ├─ Suggested Fix (expanded)
                  │     └─ Verification Status
                  │
                  ├─ LogsTab
                  │  └─ Tool Call Items (expandable)
                  │     ├─ Tool Name
                  │     ├─ Duration
                  │     ├─ Timestamp
                  │     ├─ Input JSON (expanded)
                  │     └─ Output JSON (expanded)
                  │
                  └─ EventsTab
                     └─ Event Items
                        ├─ Timestamp
                        ├─ Agent ID
                        └─ Event Type
```

---

## Data Flow - Home to Analysis

```
User Interaction
    │
    ├─ [Upload File]
    │  │
    │  ├─ File Input Handler
    │  ├─ FileReader API
    │  ├─ File Validation (1MB limit)
    │  │
    │  └─ setFileName(filename)
    │     setCodeContent(fileContent)
    │     setUiMode('editor')
    │     └─ Store Updated
    │
    └─ [Write Code]
       │
       └─ setFileName('untitled.js')
          setCodeContent('')
          setUiMode('editor')
          └─ Store Updated
                │
                ▼
        IDEInterface Renders
        (subscribes to store)
                │
        ┌──────┼──────┐
        │      │      │
        ▼      ▼      ▼
    Toolbar Editor Terminal
    RPanel
        │
        └─ All components read from store:
           codeContent, fileName, terminalLogs,
           findings, toolCalls, events
```

---

## Analysis Flow - User Perspective

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CODE READY                                                   │
│    ┌─────────────────────────────────────┐                     │
│    │ Code Editor: User's code displayed  │                     │
│    │ Terminal: Empty (ready)             │                     │
│    │ Results: Empty (no findings yet)    │                     │
│    └─────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ User clicks "Analyze" button
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. ANALYSIS STARTED                                             │
│    ┌─────────────────────────────────────┐                     │
│    │ Terminal: "$ Analyzing: file.js"    │                     │
│    │           "Starting review..."      │                     │
│    │ Results: Still empty (processing)   │                     │
│    │ Button: "Analyze" → "Stop" (red)    │                     │
│    └─────────────────────────────────────┘                     │
│                                                                  │
│    Backend:                                                      │
│    └─ Coordinator starts                                       │
│    └─ Plan created                                             │
│    └─ Agents begin analysis                                    │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ Events stream via WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. FINDINGS DISCOVERED                                          │
│    ┌─────────────────────────────────────┐                     │
│    │ Terminal:                           │                     │
│    │  "Security check in progress..."    │                     │
│    │  "Bug detection running..."         │                     │
│    │                                     │                     │
│    │ Results Panel:                      │                     │
│    │ Findings appear as they're found:   │                     │
│    │  🔴 Critical: SQL Injection         │                     │
│    │  🟠 High: XSS Vulnerability        │                     │
│    │  🟡 Medium: Race Condition         │                     │
│    │                                     │                     │
│    │ Events Tab: Agent activities       │                     │
│    │ Logs Tab: Tool calls recorded      │                     │
│    └─────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ Final events received
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. ANALYSIS COMPLETE                                            │
│    ┌─────────────────────────────────────┐                     │
│    │ Terminal: "Analysis complete"       │                     │
│    │ Results Panel: All findings shown   │                     │
│    │ Button: "Stop" → "Analyze" (blue)   │                     │
│    │                                     │                     │
│    │ User can now:                       │                     │
│    │ • Expand findings for details       │                     │
│    │ • View suggested fixes              │                     │
│    │ • Check tool logs                   │                     │
│    │ • Review events                     │                     │
│    │ • Reset and analyze new code        │                     │
│    └─────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## State Management Flow

```
Store (Zustand)
│
├─ UI State
│  ├─ uiMode: 'home' | 'editor'
│  │  └─ Used by: App.tsx (routing)
│  │
│  ├─ codeContent: string
│  │  └─ Used by: CodeEditor, IDEToolbar
│  │
│  ├─ fileName: string
│  │  └─ Used by: IDEToolbar
│  │
│  └─ theme: 'light' | 'dark'
│     └─ Used by: Document root class
│
├─ Terminal State
│  └─ terminalLogs: string[] (last 100)
│     └─ Used by: Terminal, IDEToolbar
│
├─ Results State
│  ├─ findings: Finding[]
│  │  └─ Used by: ResultsPanel (Findings Tab)
│  │
│  ├─ toolCalls: ToolCall[]
│  │  └─ Used by: ResultsPanel (Logs Tab)
│  │
│  └─ events: StreamEvent[]
│     └─ Used by: ResultsPanel (Events Tab)
│
├─ Agent State
│  ├─ agents: Map<AgentType, AgentState>
│  │  └─ Used by: Existing components
│  │
│  └─ plan: PlanStep[]
│     └─ Used by: Existing components
│
└─ Connection State
   ├─ isConnected: boolean
   │  └─ Used by: IDEToolbar (status indicator)
   │
   └─ selectedFindingId?: string
      └─ Used by: ResultsPanel
```

---

## Component Communication

```
CodeEditor
    │ onChange
    ├──────────────────▶ Store: setCodeContent()
    │                         │
    │                         └──▶ All components listening
    │                             to codeContent re-render
    │
    └─ Reads from Store:
       codeContent (to display)

Terminal
    │
    ├─ addTerminalLog() called from:
    │  ├─ IDEToolbar (on Analyze click)
    │  ├─ Backend events (via WebSocket)
    │  └─ Error handlers
    │
    └─ Reads from Store:
       terminalLogs (to display)

ResultsPanel
    │
    ├─ Reads from Store:
    │  ├─ findings (Findings Tab)
    │  ├─ toolCalls (Logs Tab)
    │  └─ events (Events Tab)
    │
    └─ Updates from:
       Backend via WebSocket
       └─ addFinding()
       └─ addToolCall()
       └─ addEvent()

IDEToolbar
    │
    ├─ onClick="Analyze"
    │  ├─ addTerminalLog('$ Analyzing...')
    │  └─ Call backend API
    │
    ├─ onClick="Reset"
    │  ├─ setCodeContent('')
    │  └─ clearTerminalLogs()
    │
    ├─ onClick="Home"
    │  └─ setUiMode('home')
    │
    └─ onClick="Theme"
       └─ toggleTheme()
```

---

## File Upload Process

```
User selects file
    │
    ▼
<input type="file"> trigger
    │
    ▼
FileReader.readAsText()
    │
    ▼
File content validation
    │
    ├─ Size check (1MB limit)
    │  └─ if > 1MB: Alert, return
    │
    ├─ Type check (optional)
    │  └─ JavaScript, Python, Java, etc.
    │
    └─ ✓ Valid
       │
       ▼
    Store updates:
    ├─ setFileName(file.name)
    ├─ setCodeContent(fileContent)
    └─ setUiMode('editor')
       │
       ▼
    HomeScreen unmounts
    IDEInterface mounts
    │
    ▼
Code displayed in editor
with line numbers and
syntax highlighting
```

---

## Results Panel Data Structure

```
ResultsPanel
│
├─ Findings Tab
│  │
│  └─ store.findings: Finding[]
│     │
│     ├─ Finding {
│     │  ├─ id: string
│     │  ├─ agent_id: AgentType
│     │  ├─ severity: 'critical'|'high'|'medium'|'low'|'info'
│     │  ├─ category: string
│     │  ├─ line?: number
│     │  ├─ description: string
│     │  ├─ details?: string
│     │  ├─ proposedFix?: string
│     │  └─ fixVerified?: boolean
│     │  }
│     │
│     └─ Rendered as:
│        ├─ [ICON] Category    Severity    Line#
│        │  Description
│        │  [Expandable]
│        │  └─ Details
│        │  └─ Suggested Fix (code block)
│        │  └─ ✓ Verified
│        │
│        └─ [Next Finding...]
│
├─ Logs Tab
│  │
│  └─ store.toolCalls: ToolCall[]
│     │
│     ├─ ToolCall {
│     │  ├─ id: string
│     │  ├─ agent_id: AgentType
│     │  ├─ tool_name: string
│     │  ├─ input: Record<string, any>
│     │  ├─ output?: Record<string, any>
│     │  ├─ duration_ms?: number
│     │  └─ timestamp: string
│     │  }
│     │
│     └─ Rendered as:
│        ├─ [tool_name]  duration  timestamp
│        │  [Expandable]
│        │  ├─ Input: JSON
│        │  └─ Output: JSON
│        │
│        └─ [Next Tool Call...]
│
└─ Events Tab
   │
   └─ store.events: StreamEvent[]
      │
      ├─ StreamEvent {
      │  ├─ event_type: string
      │  ├─ agent_id: AgentType
      │  ├─ timestamp: string
      │  ├─ event_id: string
      │  └─ data: Record<string, any>
      │  }
      │
      └─ Rendered as:
         ├─ timestamp  agent_id  event_type
         │
         └─ [Next Event...]
         (newest first)
```

---

## Split Pane Interaction

```
SplitPane Component
│
├─ Props
│  ├─ orientation: 'horizontal' | 'vertical'
│  ├─ defaultSize: number (50)
│  ├─ minSize: number (20)
│  ├─ maxSize: number (80)
│  └─ children: [ReactNode, ReactNode]
│
├─ Mouse Events
│  │
│  ├─ onMouseDown (on divider)
│  │  └─ isResizing = true
│  │
│  ├─ onMouseMove (on container)
│  │  ├─ Calculate new percentage
│  │  ├─ Constrain with min/max
│  │  └─ setSize(newSize)
│  │
│  └─ onMouseUp
│     └─ isResizing = false
│
└─ Rendering
   │
   ├─ Pane 1: width/height = size%
   ├─ Divider: 4px wide, hover effect
   └─ Pane 2: width/height = (100-size)%

   On resize:
   ├─ Cursor changes
   ├─ Divider highlights (blue)
   └─ Panes adjust smoothly
```

---

## Event Streaming Architecture

```
Backend
├─ Agent executes
├─ Event generated (e.g., finding_discovered)
└─ Sent via WebSocket

                    WebSocket
                        │
                        ▼
Frontend (useWebSocket hook)
├─ Receive event
├─ Parse JSON
└─ Dispatch to store

                    Store (Zustand)
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
    ▼                   ▼                   ▼
 addEvent()         addFinding()         updateAgentStatus()
   │                   │                   │
   └─────────┬─────────┴─────────┬─────────┘
             │                   │
    ┌────────▼───────────────────▼────────┐
    │   Components re-render (auto)        │
    │   via Zustand subscriptions          │
    └────────┬───────────────────┬────────┘
             │                   │
    ┌────────▼──────┐  ┌────────▼──────┐
    │ ResultsPanel  │  │    Terminal   │
    │ Shows new     │  │ Shows log     │
    │ finding       │  │ (if logged)   │
    └───────────────┘  └───────────────┘
```

---

## Styling Layer

```
Tailwind CSS
    │
    ├─ Configuration (tailwind.config.js)
    │  ├─ Dark mode: class-based
    │  ├─ Color extends: slate, blue, red, etc.
    │  └─ Animations: fade-in, slide-up
    │
    ├─ Global CSS
    │  └─ Applied via index.html dark class
    │
    └─ Component Classes
       │
       ├─ CodeEditor
       │  ├─ bg-slate-950 (background)
       │  ├─ text-slate-100 (text)
       │  ├─ font-mono (monospace)
       │  └─ Various utilities
       │
       ├─ Terminal
       │  ├─ bg-slate-900 (panel)
       │  ├─ text-slate-300 (text)
       │  └─ Scrollable styling
       │
       ├─ ResultsPanel
       │  ├─ Border colors
       │  ├─ Tab styling
       │  ├─ Severity colors
       │  └─ Hover effects
       │
       └─ SplitPane
          ├─ Divider styling
          ├─ Cursor changes
          └─ Transition effects
```

---

## Browser Rendering Pipeline

```
User Input
    │
    ▼
React Event Handler
    │
    ├─ Update Store (Zustand)
    │
    ├─ Re-render Components
    │  (only affected components)
    │
    ├─ Update Virtual DOM
    │
    ├─ Compare with Real DOM
    │
    └─ Apply minimal patches
       │
       ▼
    Browser Paint
    │
    ├─ Tailwind classes applied
    ├─ CSS computed
    ├─ Layout calculated
    │
    ▼
Browser Display Updated
    │
    ▼
User sees new content
```

---

## Performance Considerations

```
Optimization Strategies
│
├─ State Management
│  ├─ Zustand (minimal re-renders)
│  ├─ Selective subscriptions
│  └─ Memoized computations
│
├─ Component Structure
│  ├─ Small focused components
│  ├─ Lazy component loading (ready)
│  └─ Split panes isolation
│
├─ Data Management
│  ├─ Terminal: 100 logs max
│  ├─ Events: 1000 max
│  ├─ Tool calls: 500 max
│  ├─ Thoughts: 200 max
│  └─ Auto-cleanup prevents bloat
│
├─ Styling
│  ├─ Tailwind utility-first
│  ├─ No inline styles
│  └─ CSS pruning in build
│
└─ Future Optimizations
   ├─ Virtual scrolling (for large lists)
   ├─ Code splitting
   ├─ Lazy loading
   └─ Service workers
```

---

**These diagrams provide a visual understanding of the IDE system architecture and should help with onboarding and future development.**
