# IDE-Style UI for Code Review System

A professional, VS Code-inspired interface for the code review system with split-pane layout, real-time analysis, and comprehensive results presentation.

## Architecture Overview

### UI Modes

The application has two primary modes:

1. **Home Screen** (`uiMode: 'home'`)
   - Initial landing page
   - Two entry points: Upload file or Write code
   - Beautiful onboarding experience with Framer Motion animations

2. **IDE Interface** (`uiMode: 'editor'`)
   - Main analysis interface
   - Three-panel layout: Editor + Terminal + Results

## Component Structure

### Core Components

#### `HomeScreen.tsx`
The landing page with file upload and code editor options.

**Features:**
- File upload with validation (checks file size)
- Direct code editor entry
- Beautiful animated UI with Framer Motion
- File type support: `.js`, `.ts`, `.jsx`, `.tsx`, `.py`, `.java`, etc.

**Key Props:**
- Uses global store to transition to editor mode
- Sets initial file name and code content

#### `IDEInterface.tsx`
Main layout orchestrator combining all three panels.

**Layout:**
- Split pane vertical layout
- Left side: Code Editor (60% default) + Terminal (40% default)
- Right side: Results Panel (fixed 384px width)

#### `CodeEditor.tsx`
Syntax-highlighted code editor with line numbers.

**Features:**
- Real-time code input with line number display
- Basic syntax highlighting for:
  - Keywords (blue: `function`, `const`, `if`, etc.)
  - Strings (green: quoted text)
  - Comments (gray: `//` and `/* */`)
  - Numbers (amber: numeric literals)
- Monospace font for code readability
- Full height utilization

**Future Enhancement:**
- Integration with Monaco Editor for production-grade features
- Custom language support
- Code folding
- Minimap

#### `Terminal.tsx`
Terminal/console emulator for analysis logs and output.

**Features:**
- Scrollable log output
- Auto-scroll to bottom on new logs
- Clear button for cleanup
- macOS-style window controls (visual only)
- Stores up to 100 recent logs
- Auto-scrolling indicator button

**Output Examples:**
- `$ Analyzing: filename.js`
- `Starting code review...`
- Analysis status and completion messages

#### `ResultsPanel.tsx`
Displays analysis results across three tabs.

**Tabs:**

1. **Findings Tab**
   - Expandable finding cards
   - Color-coded severity: Critical (red), High (orange), Medium (yellow), Low (blue), Info (gray)
   - Displays:
     - Category and severity level
     - Line number (if available)
     - Description
     - Details (expandable)
     - Suggested fix code (expandable)
     - Fix verification status

2. **Logs Tab**
   - Tool call history (reversed, newest first)
   - Expandable for input/output details
   - Shows execution duration
   - Displays timestamp

3. **Events Tab**
   - Stream of all events
   - Timestamps
   - Agent ID
   - Event type
   - Chronologically sorted

#### `SplitPane.tsx`
Reusable resizable split pane component.

**Features:**
- Horizontal and vertical orientation support
- Mouse drag to resize
- Min/max size constraints
- Visual feedback on hover
- Smooth transitions

**Usage:**
```tsx
<SplitPane orientation="vertical" defaultSize={60} minSize={30} maxSize={80}>
  <PaneOne />
  <PaneTwo />
</SplitPane>
```

#### `IDEToolbar.tsx`
Top toolbar with file info, connection status, and controls.

**Features:**
- File name display with monospace font
- Connection status indicator (animated green or red)
- Controls:
  - **Analyze**: Starts code review (blue button)
  - **Stop**: Halts ongoing analysis (red, when running)
  - **Reset**: Clears all data
- Theme toggle (Sun/Moon icon)
- Home button for navigation

## State Management (Zustand Store)

### IDE-Specific Store Properties

```typescript
// UI Mode
uiMode: 'home' | 'editor'
setUiMode: (mode) => void

// Code Content
codeContent: string
setCodeContent: (content) => void
fileName: string
setFileName: (name) => void

// Terminal Logs
terminalLogs: string[]
addTerminalLog: (log) => void
clearTerminalLogs: () => void
```

### Existing Store Properties (still available)

- `findings`: Finding[]
- `toolCalls`: ToolCall[]
- `events`: StreamEvent[]
- `agents`: Map<AgentType, AgentState>
- `theme`: 'light' | 'dark'
- `isConnected`: boolean

## Styling System

### Color Palette (Dark Mode)

**Backgrounds:**
- `bg-slate-950`: Deepest black (main background)
- `bg-slate-900`: Dark gray (panels, headers)
- `bg-slate-800`: Medium dark (hover states)

**Text:**
- `text-slate-100`: Bright white (primary)
- `text-slate-300`: Light gray (secondary)
- `text-slate-400`: Medium gray (tertiary)
- `text-slate-500`: Darker gray (disabled, subtle)

**Accents:**
- `text-blue-400` / `bg-blue-600`: Primary action
- `text-blue-300`: Hover state
- Severity colors (red, orange, yellow, green)

**Borders:**
- `border-slate-700`: Main dividers
- `border-slate-800`: Secondary dividers

### Design Principles

1. **Minimal Whitespace**: Maximum content area utilization
2. **High Contrast**: Light text on dark background for readability
3. **Professional Aesthetic**: Subtle animations, smooth transitions
4. **Accessibility**: Clear semantic HTML, sufficient color contrast
5. **Consistency**: Unified spacing, typography, and component patterns

## Integration Points

### With Backend

The IDE connects to your backend through:

1. **WebSocket Connection** (`useWebSocket` hook)
   - Real-time streaming events
   - Agent status updates
   - Live findings and logs

2. **Mock Events** (`useMockEvents` hook)
   - Development/demo mode
   - Simulates full analysis workflow
   - Disabled in production

### Event Flow

```
User Upload/Paste Code
    ↓
Terminal: "Analyzing: filename.js"
    ↓
Store: codeContent updated
    ↓
Backend Analysis Started
    ↓
WebSocket Events → Store → Components Update
    ↓
Terminal: Status updates
Results Panel: Findings appear
    ↓
Analysis Complete
```

## File Organization

```
src/
├── components/
│   ├── CodeEditor.tsx          # Code input with line numbers
│   ├── Terminal.tsx             # Console output
│   ├── ResultsPanel.tsx         # Findings, logs, events tabs
│   ├── SplitPane.tsx            # Resizable pane divider
│   ├── IDEToolbar.tsx           # Top toolbar
│   ├── IDEInterface.tsx         # Main layout
│   ├── HomeScreen.tsx           # Landing page
│   ├── Header.tsx               # (Existing header)
│   ├── AgentStatusPanel.tsx     # (Existing components)
│   └── ... (other existing components)
├── store.ts                     # Zustand store (extended)
├── types.ts                     # Type definitions
├── hooks/
│   ├── useWebSocket.ts
│   ├── useMockEvents.ts
│   └── ... (other hooks)
├── App.tsx                      # Route between home/editor
└── main.tsx
```

## Usage Instructions

### For End Users

1. **Start Application**
   - Opens to Home Screen
   - Choose "Upload File" or "Write Code"

2. **Upload File**
   - Click "Upload File" button
   - Select a code file from computer
   - Editor populated automatically
   - Transitions to IDE Interface

3. **Write Code**
   - Click "Write Code" button
   - Opens blank editor
   - Paste or type code
   - Can be analyzed immediately

4. **Analyze Code**
   - Click blue "Analyze" button
   - Terminal shows progress
   - Results appear in right panel
   - Expand findings to see details

5. **Navigate Results**
   - Switch between Findings/Logs/Events tabs
   - Click finding to expand details
   - View suggested fixes

### For Developers

#### Adding Custom Syntax Highlighting

Edit `CodeEditor.tsx` `highlightLine` function:

```typescript
function highlightLine(line: string): string {
  // Add new patterns
  highlighted = highlighted.replace(
    /your_pattern/g,
    '<span class="your-color">$1</span>'
  )
  return highlighted
}
```

#### Integrating with Backend

Update `IDEToolbar.tsx` `handleRun` function to call your backend:

```typescript
const handleRun = async () => {
  setIsRunning(true)
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: JSON.stringify({ code: codeContent })
    })
    // Handle response...
  } finally {
    setIsRunning(false)
  }
}
```

#### Customizing Colors

Modify `tailwind.config.js`:

```javascript
colors: {
  slate: {
    950: '#0f172a',  // Change background
    900: '#1e293b',  // Change panel
  }
}
```

## Performance Considerations

1. **Code Editor**
   - Handles up to ~1MB files (user-facing validation at 1MB)
   - Line number rendering scales with content
   - Consider virtualizing for very large files

2. **Results Panel**
   - Stores up to 100 terminal logs
   - Stores up to 500 tool calls
   - Stores up to 200 thoughts
   - Maintains up to 1000 events
   - Auto-cleanup prevents memory growth

3. **Terminal Auto-scroll**
   - Smooth scroll to bottom on new logs
   - Manual scroll button for user control

4. **Split Pane Resizing**
   - Uses CSS transforms for smooth dragging
   - Debounced to avoid excessive re-renders

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 15+
- All modern browsers with ES2020+ support

## Accessibility Features

- Semantic HTML structure
- High contrast color scheme (WCAG AA compliant)
- Keyboard navigation support
- ARIA labels on interactive elements
- Clear visual feedback on focus/hover states

## Future Enhancements

1. **Monaco Editor Integration**
   - Professional syntax highlighting
   - Code folding
   - Minimap
   - Bracket matching

2. **Advanced Features**
   - Diff view for suggested fixes
   - File tree for multi-file analysis
   - Search in findings
   - Export results

3. **Performance**
   - Virtual scrolling for large result sets
   - Lazy loading of event details
   - Code splitting for components

4. **Collaboration**
   - Real-time multi-user editing
   - Commenting on findings
   - Sharing analysis reports

## Troubleshooting

### Terminal Not Scrolling

Check that `scrollRef` is properly attached and terminal logs are being added.

### Results Panel Not Updating

Verify Zustand store methods are being called. Check browser console for errors.

### Split Pane Not Resizing

Ensure mouse events are not being prevented elsewhere. Check for event.preventDefault() calls.

### Syntax Highlighting Not Working

The included highlighter is basic. For production, integrate Monaco Editor or similar.

## License

Part of the Code Review System project.
