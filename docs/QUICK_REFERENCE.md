# Quick Reference - Minimal IDE UI

## Getting Started

### Install & Run
```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173` with mock events.

### Build for Production
```bash
npm run build
npm run preview  # Test production build locally
```

---

## Color System

### Usage
Use Tailwind utility classes with custom color names:

```jsx
// Text
<span className="text-code-text">Primary text</span>
<span className="text-code-text-secondary">Secondary</span>
<span className="text-code-text-muted">Muted text</span>

// Backgrounds
<div className="bg-code-bg">Pure black</div>
<div className="bg-code-bg-subtle">Subtle black</div>
<div className="bg-code-surface">Hover background</div>

// Accents
<button className="bg-code-accent hover:bg-code-accent-hover">
  Blue accent button
</button>

// Semantic
<span className="text-critical-500">Error</span>
<span className="text-success-500">Success</span>
<span className="text-warning-500">Warning</span>
<span className="text-info-500">Info</span>
```

### Color Reference
```
Primary:    bg-code-bg (#000000)
Subtle:     bg-code-bg-subtle (#0a0a0a)
Surface:    bg-code-surface (#1a1a1a)
Border:     border-code-border (#2a2a2a)

Text:       text-code-text (#e0e0e0)
Secondary:  text-code-text-secondary (#d4d4d4)
Muted:      text-code-text-muted (#808080)

Accent:     bg-code-accent (#4a9eff)
Hover:      hover:bg-code-accent-hover (#5ba3ff)
Dark:       bg-code-accent-dark (#3b82ce)
```

---

## Common Patterns

### Card/Container
```jsx
<div className="bg-code-bg-subtle border border-code-border rounded p-4">
  Content
</div>
```

### Button Primary
```jsx
<button className="bg-code-accent hover:bg-code-accent-hover
                   text-code-bg font-semibold px-4 py-2 rounded
                   focus:outline-none focus:ring-2 focus:ring-code-accent">
  Analyze
</button>
```

### Button Secondary
```jsx
<button className="text-code-text hover:text-code-accent
                   hover:bg-code-surface px-3 py-2 rounded
                   transition-colors">
  Cancel
</button>
```

### Input Field
```jsx
<input className="bg-code-bg border border-code-border
                  text-code-text placeholder-code-text-muted
                  px-3 py-2 rounded focus:ring-2 focus:ring-code-accent" />
```

### Status Indicator
```jsx
<div className="flex items-center gap-2">
  <div className="w-2 h-2 rounded-full bg-success-500 animate-pulse-subtle" />
  <span className="text-code-text-muted">Connected</span>
</div>
```

### Code Block
```jsx
<pre className="bg-code-bg-subtle border border-code-border
               text-code-text-secondary p-4 rounded
               font-mono text-sm overflow-x-auto">
  {code}
</pre>
```

### Divider/Border
```jsx
<div className="border-t border-code-border my-4" />
```

---

## Component API

### useStore Hook
```jsx
import { useStore } from './store'

const {
  // Agent state
  agents,
  updateAgentStatus,

  // Events
  events,
  addEvent,
  clearEvents,

  // Findings
  findings,
  addFinding,
  updateFinding,

  // Tool calls
  toolCalls,
  addToolCall,

  // Thoughts
  thoughts,
  addThought,

  // Plan
  plan,
  setPlan,
  updatePlanStep,

  // Session
  isConnected,
  setConnected,
  currentReviewId,
  setCurrentReviewId,

  // UI
  theme,
  toggleTheme,
  selectedFindingId,
  setSelectedFindingId,

  // IDE
  uiMode,
  setUiMode,
  codeContent,
  setCodeContent,
  fileName,
  setFileName,
  terminalLogs,
  addTerminalLog,
  clearTerminalLogs,
} = useStore()
```

### Component Props

#### HomeScreen
```jsx
<HomeScreen />
// No props - uses store directly
```

#### IDEInterface
```jsx
<IDEInterface />
// No props - uses store directly
```

#### IDEToolbar
```jsx
<IDEToolbar
  onRun={() => {}}
  onStop={() => {}}
  onReset={() => {}}
/>
```

#### CodeEditor
```jsx
<CodeEditor className="optional-class" />
```

#### Terminal
```jsx
<Terminal className="optional-class" />
```

#### ResultsPanel
```jsx
<ResultsPanel className="optional-class" />
```

#### SplitPane
```jsx
<SplitPane
  orientation="vertical"  // or "horizontal"
  defaultSize={60}        // percentage (0-100)
  minSize={20}           // minimum percentage
  maxSize={80}           // maximum percentage
>
  <FirstPane />
  <SecondPane />
</SplitPane>
```

---

## State Management

### Add Finding
```jsx
useStore().addFinding({
  id: 'finding-1',
  agent_id: 'security_agent',
  severity: 'critical',
  category: 'SQL Injection',
  line: 42,
  description: 'Unsafe query with user input',
  details: 'XPath-based SQL without parameterization',
  proposedFix: "db.prepare(sql).bind(user_input)",
  fixVerified: false,
})
```

### Add Tool Call
```jsx
useStore().addToolCall({
  id: 'tool-1',
  agent_id: 'security_agent',
  tool_name: 'analyze_code',
  input: { code: '...' },
  output: { findings: [...] },
  duration_ms: 1234,
  timestamp: new Date().toISOString(),
})
```

### Add Thought
```jsx
useStore().addThought({
  id: 'thought-1',
  agent_id: 'security_agent',
  content: 'Found potential SQL injection at line 42',
  timestamp: new Date().toISOString(),
})
```

### Add Terminal Log
```jsx
useStore().addTerminalLog('$ Analyzing code...')
useStore().addTerminalLog('Error: Invalid syntax at line 10')
```

### Switch UI Mode
```jsx
// Go to IDE
useStore().setUiMode('editor')

// Go to home
useStore().setUiMode('home')
```

---

## Animations

### Entrance Animation
```jsx
import { motion } from 'framer-motion'

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  Content
</motion.div>
```

### Staggered Children
```jsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 }
}

<motion.div variants={containerVariants} initial="hidden" animate="visible">
  <motion.div variants={itemVariants}>Item 1</motion.div>
  <motion.div variants={itemVariants}>Item 2</motion.div>
</motion.div>
```

### Hover Animation
```jsx
<motion.div
  whileHover={{ scale: 1.05 }}
  transition={{ duration: 0.2 }}
>
  Hover me
</motion.div>
```

---

## Keyboard Focus

### Focus Ring
```jsx
<button className="focus:outline-none focus:ring-2 focus:ring-code-accent">
  Button
</button>
```

### Focus Visible (Only on keyboard)
```jsx
<button className="focus-visible:ring-2 focus-visible:ring-code-accent">
  Button
</button>
```

---

## Responsive Classes

### Conditional Styling
```jsx
// Mobile first
<div className="text-sm md:text-base lg:text-lg">
  Responsive text
</div>

// Full-width on mobile, half on tablet+
<div className="w-full md:w-1/2">
  Responsive width
</div>

// Single column mobile, 2 columns tablet+
<div className="grid grid-cols-1 md:grid-cols-2">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

---

## Icons

### Lucide React Icons
```jsx
import { Upload, FileText, Zap, Play, Square, AlertCircle } from 'lucide-react'

<Upload size={20} strokeWidth={1.5} className="text-code-accent" />
<Play size={14} strokeWidth={2} />
<AlertCircle size={16} />
```

### Common Icon Sizes
```
Navigation:     16-20px
Buttons:        14-16px
Sections:       20-24px
Hero:           32-48px
Inline:         14px
```

---

## File Upload

### Using File Input
```jsx
import { useRef } from 'react'
import { useStore } from '../store'

const fileInputRef = useRef<HTMLInputElement>(null)

const handleUpload = (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (event) => {
    useStore().setFileName(file.name)
    useStore().setCodeContent(event.target?.result)
    useStore().setUiMode('editor')
  }
  reader.readAsText(file)
}

return (
  <>
    <input
      ref={fileInputRef}
      type="file"
      onChange={handleUpload}
      className="hidden"
      accept=".js,.ts,.jsx,.tsx,.py,.java,.cpp,.go,.rs"
    />
    <button onClick={() => fileInputRef.current?.click()}>
      Upload File
    </button>
  </>
)
```

---

## Common Tasks

### Change Theme
```jsx
const { toggleTheme } = useStore()
<button onClick={toggleTheme}>Toggle Theme</button>
```

### Display Finding Severity
```jsx
const severityConfig = {
  critical: { color: 'text-critical-500', label: 'Critical' },
  high: { color: 'text-orange-400', label: 'High' },
  medium: { color: 'text-warning-500', label: 'Medium' },
  low: { color: 'text-info-500', label: 'Low' },
}

const config = severityConfig[finding.severity]
<span className={config.color}>{config.label}</span>
```

### Auto-Scroll Terminal
```jsx
import { useRef, useEffect } from 'react'

const scrollRef = useRef<HTMLDivElement>(null)

useEffect(() => {
  if (scrollRef.current) {
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }
}, [logs])

return <div ref={scrollRef} className="overflow-y-auto">...</div>
```

### Expandable Section
```jsx
import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import clsx from 'clsx'

const [expanded, setExpanded] = useState(false)

return (
  <>
    <button onClick={() => setExpanded(!expanded)}>
      <span>Title</span>
      <ChevronDown className={clsx('transition-transform', {
        'rotate-180': expanded
      })} />
    </button>
    {expanded && <div>Details</div>}
  </>
)
```

---

## Debug Tips

### Check Store State
```jsx
import { useStore } from './store'

export function Debug() {
  const store = useStore()
  return <pre>{JSON.stringify(store, null, 2)}</pre>
}
```

### Log Events
```jsx
useStore().addEvent(event)
console.log(useStore().events)
```

### Monitor Performance
```bash
# Check bundle size
npm run build

# View performance in DevTools
# Go to: DevTools > Performance > Record > (interact) > Stop
```

---

## Environment Variables

### Development
```bash
npm run dev
# Default: http://localhost:5173
# Uses mock events
# No backend required
```

### Production
```bash
npm run build
# Creates dist/ directory
# Ready for deployment
```

### Configuration
Create `.env.production`:
```
VITE_API_URL=https://api.example.com
```

---

## Deployment

### Static Hosting
```bash
# Build
npm run build

# Deploy dist/ to your server
scp -r dist/* user@server:/var/www/code-review/
```

### Docker
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Vercel
```bash
npm install -g vercel
vercel
# Follow prompts
```

---

## Troubleshooting

### Build Fails
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Styles Not Applied
```bash
# Check if Tailwind config is correct
# Verify class names match customized colors
# Clear Tailwind cache
rm -rf .next node_modules/.cache
npm run build
```

### Dev Server Won't Start
```bash
# Check if port 5173 is in use
lsof -i :5173

# Try different port
npm run dev -- --port 3000
```

### Performance Issues
```bash
# Check bundle size
npm run build
# Use DevTools Performance tab
# Profile with Chrome DevTools
```

---

## Resources

- **React**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **Framer Motion**: https://www.framer.com/motion
- **Zustand**: https://github.com/pmndrs/zustand
- **Vite**: https://vitejs.dev
- **Lucide Icons**: https://lucide.dev

---

## Contact

For questions or issues, refer to:
- `MINIMAL_IDE_DESIGN.md` - Full design documentation
- `IDE_STYLE_GUIDE.md` - Visual reference and specifications
- Component files - Inline TypeScript comments
- Tailwind config - Color and animation definitions

---

**Version**: 1.0
**Last Updated**: 2026-03-25
**Status**: Production Ready ✅
