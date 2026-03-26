# Component Reference Guide

Complete reference for all IDE components with examples and API documentation.

---

## HomeScreen Component

**File**: `src/components/HomeScreen.tsx`

The landing page with file upload and code entry options.

### Usage

```tsx
import { HomeScreen } from './components/HomeScreen'

function App() {
  return <HomeScreen />
}
```

### Props

None. Uses Zustand store directly.

### Store Interactions

```typescript
const { setUiMode, setCodeContent, setFileName } = useStore()

// Triggered by upload
setFileName('myfile.js')
setCodeContent(fileContent)
setUiMode('editor')

// Triggered by "Write Code"
setFileName('untitled.js')
setCodeContent('')
setUiMode('editor')
```

### Features

- 🎨 Beautiful landing page with animations
- 📁 File upload with validation
- ✍️ Direct code editor entry
- 🎬 Framer Motion animations
- 📱 Fully responsive

### Styling

Dark mode with blue accents:
- Background: `bg-slate-950`
- Panels: `bg-slate-900`
- Buttons: `bg-blue-600`

---

## IDEInterface Component

**File**: `src/components/IDEInterface.tsx`

Main layout orchestrator combining editor, terminal, and results.

### Usage

```tsx
import { IDEInterface } from './components/IDEInterface'

function App() {
  return <IDEInterface />
}
```

### Props

None. Manages children internally.

### Layout

```
IDEInterface
├── IDEToolbar
└── Main Content Area (flex row)
    ├── Left Column (flex-1, vertical split)
    │   ├── CodeEditor (60%)
    │   ├── SplitPane Divider
    │   └── Terminal (40%)
    └── Right Column (w-96)
        └── ResultsPanel
```

### Key Methods

```typescript
const handleReset = () => {
  setCodeContent('')
  clearTerminalLogs()
}
```

---

## CodeEditor Component

**File**: `src/components/CodeEditor.tsx`

Syntax-highlighted code editor with line numbers.

### Usage

```tsx
import { CodeEditor } from './components/CodeEditor'

<CodeEditor className="border-2 border-blue-500" />
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `className` | string | `''` | Additional CSS classes |

### Store Usage

```typescript
const { codeContent, setCodeContent } = useStore()

// Real-time updates on user input
<textarea
  value={codeContent}
  onChange={(e) => setCodeContent(e.target.value)}
/>
```

### Features

- 📝 Automatic line numbering
- 🎨 Syntax highlighting for:
  - Keywords (blue)
  - Strings (green)
  - Comments (gray)
  - Numbers (amber)
- 🖥️ Monospace font
- ⌨️ Full keyboard support

### Styling Classes

```css
/* Line number column */
.bg-slate-900 border-r border-slate-700 px-4 py-4
text-right font-mono text-xs text-slate-500

/* Code textarea */
.bg-slate-950 text-slate-100 font-mono text-sm
p-4 focus:outline-none focus:ring-0 border-0
```

### Syntax Highlighting

Edit the `highlightLine()` function to customize:

```typescript
function highlightLine(line: string): string {
  // Keywords
  highlighted = highlighted.replace(
    /\b(keyword1|keyword2)\b/g,
    '<span class="text-blue-400">$1</span>'
  )

  // Add more patterns as needed
  return highlighted
}
```

### Supported Languages

Works with any language, but highlighting is basic:
- JavaScript/TypeScript
- Python
- Java
- C/C++
- Go
- Rust
- SQL
- And more...

---

## Terminal Component

**File**: `src/components/Terminal.tsx`

Console/terminal emulator for agent output.

### Usage

```tsx
import { Terminal } from './components/Terminal'

<Terminal className="border border-slate-700" />
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `className` | string | `''` | Additional CSS classes |

### Store Usage

```typescript
const { terminalLogs, addTerminalLog, clearTerminalLogs } = useStore()

// Add a log entry
addTerminalLog('Analysis starting...')

// Clear all logs
clearTerminalLogs()
```

### Log Format

```typescript
// Simple text logs
addTerminalLog('$ Analyzing: file.js')
addTerminalLog('Security check in progress...')

// Multi-line logs (preserved)
addTerminalLog(`Error on line 42:
  expected ; found }`)

// Timestamps handled automatically
addTerminalLog('[12:34:56] Analysis complete')
```

### Features

- 📺 Scrollable output
- 🔄 Auto-scroll to newest logs
- 🧹 Clear button
- 📦 Stores last 100 logs
- 🎨 macOS-style decorative controls

### Styling

```css
/* Header with traffic lights */
.bg-slate-900 border-b border-slate-700

/* Output area */
.bg-slate-950 text-slate-300 font-mono text-xs
overflow-y-auto

/* Status indicators */
.w-3 h-3 rounded-full
/* Red, Yellow, Green */
```

---

## ResultsPanel Component

**File**: `src/components/ResultsPanel.tsx`

Three-tab interface: Findings, Logs, Events.

### Usage

```tsx
import { ResultsPanel } from './components/ResultsPanel'

<ResultsPanel className="w-96" />
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `className` | string | `''` | Additional CSS classes |

### Store Usage

```typescript
const { findings, toolCalls, events } = useStore()

// Results automatically update from store
// No manual prop passing needed
```

### Tab: Findings

Displays security issues and bugs.

**Data Structure:**
```typescript
interface Finding {
  id: string
  agent_id: AgentType
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  category: string
  line?: number
  description: string
  details?: string
  proposedFix?: string
  fixVerified?: boolean
}
```

**Severity Colors:**
```typescript
const severityConfig = {
  critical: { color: 'text-red-400', bg: 'bg-red-950' },
  high: { color: 'text-orange-400', bg: 'bg-orange-950' },
  medium: { color: 'text-yellow-400', bg: 'bg-yellow-950' },
  low: { color: 'text-blue-400', bg: 'bg-blue-950' },
  info: { color: 'text-slate-400', bg: 'bg-slate-900' }
}
```

**Expandable Content:**
- Description
- Details (technical info)
- Suggested fix (code block)
- Verification status

### Tab: Logs

Tool call history with details.

**Data Structure:**
```typescript
interface ToolCall {
  id: string
  agent_id: AgentType
  tool_name: string
  input: Record<string, any>
  output?: Record<string, any>
  duration_ms?: number
  timestamp: string
}
```

**Display:**
- Tool name (monospace badge)
- Duration
- Timestamp
- Expandable input/output JSON

### Tab: Events

System event stream.

**Data Structure:**
```typescript
interface StreamEvent {
  event_type: string
  agent_id: AgentType
  timestamp: string
  event_id: string
  data: Record<string, any>
}
```

**Display:**
- Newest events first
- Timestamp
- Agent ID
- Event type

---

## SplitPane Component

**File**: `src/components/SplitPane.tsx`

Resizable drag-to-resize pane divider.

### Usage

```tsx
import { SplitPane } from './components/SplitPane'

<SplitPane
  orientation="vertical"
  defaultSize={60}
  minSize={30}
  maxSize={80}
>
  <LeftPane />
  <RightPane />
</SplitPane>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `orientation` | `'horizontal' \| 'vertical'` | - | Direction of split |
| `defaultSize` | number | `50` | Initial size % of first pane |
| `minSize` | number | `20` | Minimum size % |
| `maxSize` | number | `80` | Maximum size % |
| `children` | `[ReactNode, ReactNode]` | - | Two child components |

### Examples

**Vertical Split (left/right):**
```tsx
<SplitPane orientation="vertical" defaultSize={60}>
  <CodeEditor />
  <Results />
</SplitPane>
```

**Horizontal Split (top/bottom):**
```tsx
<SplitPane orientation="horizontal" defaultSize={70}>
  <Editor />
  <Terminal />
</SplitPane>
```

**Constrained Resize:**
```tsx
<SplitPane
  orientation="vertical"
  defaultSize={50}
  minSize={25}
  maxSize={75}
>
  <Component1 />
  <Component2 />
</SplitPane>
```

### Styling

```css
/* Divider line */
.w-1 hover:w-1.5        /* Vertical */
.h-1 hover:h-1.5        /* Horizontal */

/* Colors */
.bg-slate-700           /* Normal */
.hover:bg-blue-500      /* On hover */

/* Cursors */
.cursor-col-resize      /* Vertical drag */
.cursor-row-resize      /* Horizontal drag */
```

---

## IDEToolbar Component

**File**: `src/components/IDEToolbar.tsx`

Top toolbar with file info and analysis controls.

### Usage

```tsx
import { IDEToolbar } from './components/IDEToolbar'

<IDEToolbar
  onRun={() => console.log('Analyze clicked')}
  onStop={() => console.log('Stop clicked')}
  onReset={() => console.log('Reset clicked')}
/>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onRun` | function | undefined | Called when Analyze clicked |
| `onStop` | function | undefined | Called when Stop clicked |
| `onReset` | function | undefined | Called when Reset clicked |

### Store Usage

```typescript
const {
  fileName,
  isConnected,
  theme,
  toggleTheme,
  setUiMode,
  addTerminalLog
} = useStore()

// File name display
<span>{fileName}</span>

// Connection status
<div className={isConnected ? 'bg-green-500' : 'bg-red-500'} />

// Theme toggle
onClick={toggleTheme}

// Navigation
onClick={() => setUiMode('home')}
```

### Buttons

**Analyze Button:**
- Color: Blue (`bg-blue-600`)
- Disabled: When analysis running
- Logs: Terminal update
- Calls: `onRun()` callback

**Stop Button:**
- Color: Red (`bg-red-600`)
- Only shows: During analysis
- Calls: `onStop()` callback

**Reset Button:**
- Icon: `RotateCcw`
- Calls: `onReset()` callback
- Effect: Clears code and terminal

### Status Indicator

```typescript
// Connection
<div className={isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'} />
<span>{isConnected ? 'Connected' : 'Disconnected'}</span>
```

---

## Integration Examples

### Complete IDE Setup

```tsx
import { useState } from 'react'
import { useStore } from './store'
import { IDEInterface } from './components/IDEInterface'

function MyIDE() {
  const {
    codeContent,
    fileName,
    addFinding,
    addTerminalLog,
    clearTerminalLogs
  } = useStore()

  const handleAnalyze = async () => {
    try {
      addTerminalLog('$ Starting analysis...')

      // Call backend API
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: codeContent,
          fileName: fileName
        })
      })

      const data = await response.json()

      // Add findings
      data.findings.forEach(finding => {
        addFinding({
          id: finding.id,
          agent_id: 'coordinator',
          severity: finding.severity,
          category: finding.category,
          description: finding.description,
          line: finding.line
        })
      })

      addTerminalLog('$ Analysis complete!')
    } catch (error) {
      addTerminalLog(`Error: ${error.message}`)
    }
  }

  return <IDEInterface onRun={handleAnalyze} />
}
```

### Custom Terminal Output

```tsx
const { addTerminalLog } = useStore()

// Simple message
addTerminalLog('Hello, World!')

// Formatted message with timestamp
const time = new Date().toLocaleTimeString()
addTerminalLog(`[${time}] Analysis started`)

// Multi-line output
const output = `
Line 1: Security check
Line 2: Bug detection
Line 3: Complete
`.trim()
addTerminalLog(output)
```

### Adding Findings Programmatically

```tsx
const { addFinding } = useStore()

addFinding({
  id: `finding_${Date.now()}`,
  agent_id: 'security_agent',
  severity: 'critical',
  category: 'sql_injection',
  line: 45,
  description: 'SQL injection detected in query',
  details: 'User input concatenated directly into SQL',
  proposedFix: 'Use parameterized queries: db.query("SELECT * FROM users WHERE id = ?", [id])',
  fixVerified: false
})
```

---

## Styling Customization

### Tailwind Classes Used

```css
/* Dark mode */
dark:bg-slate-950
dark:text-slate-100

/* Spacing */
px-4 py-3 gap-3

/* Typography */
text-xs font-mono
text-sm font-semibold

/* Borders */
border border-slate-700
rounded-lg

/* Transitions */
transition-colors hover:bg-slate-800
```

### Modifying Colors

Edit `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      slate: {
        950: '#0f172a',  // Background
        900: '#1e293b',  // Panels
        700: '#334155',  // Borders
      },
    },
  },
}
```

### Modifying Spacing

```javascript
theme: {
  extend: {
    spacing: {
      gutter: '16px',
    },
  },
}
```

---

## Debugging Tips

### Check Store State

```typescript
const store = useStore()
console.log('Current code:', store.codeContent)
console.log('Findings:', store.findings)
console.log('Terminal logs:', store.terminalLogs)
```

### Monitor Component Renders

Add React DevTools and check:
1. Which components re-render
2. Store subscription changes
3. Props flow

### Terminal Debugging

Use the Terminal component to log:

```typescript
const { addTerminalLog } = useStore()

// Debug output
addTerminalLog(`Debug: codeContent length = ${codeContent.length}`)
addTerminalLog(`Debug: findings count = ${findings.length}`)
```

### TypeScript Errors

```bash
npm run type-check
```

Common issues:
- Missing imports
- Type mismatches
- Undefined store methods

---

## Performance Tips

1. **Split Pane**: Use `key` prop for stable identity
2. **Terminal**: Stores only last 100 logs
3. **Results**: Expandable cards to limit DOM nodes
4. **Code Editor**: Consider virtualizing for large files
5. **Store**: Zustand automatically optimizes subscriptions

---

## Best Practices

1. ✅ Use store hooks in components
2. ✅ Pass only needed props
3. ✅ Memoize expensive operations
4. ✅ Use semantic HTML
5. ✅ Test with real data
6. ✅ Check browser console
7. ✅ Use TypeScript
8. ✅ Keep components small

---

**For more help, see IDE_UI_GUIDE.md and IMPLEMENTATION_SUMMARY.md**
