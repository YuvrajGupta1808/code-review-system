# Getting Started with the Code Review UI

## 30-Second Quick Start

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 - you'll see a complete code review simulation with 5 findings!

## What You'll See

The UI shows a realistic code review in progress:

1. **Top Left**: 3 agents (Coordinator, Security, Bug) with status indicators
2. **Top Right**: Execution plan showing 6 steps, tracking progress
3. **Bottom Left**: Live thoughts from the analyzing agents
4. **Bottom Right**: Findings organized by severity with a summary grid
5. **Full Width Bottom**: Log of all tool calls with inputs/outputs

The entire simulation takes about 8.5 seconds and shows all features in action.

## Common Tasks

### I want to connect to the real backend

1. Make sure backend is running:
   ```bash
   cd backend
   python -m uvicorn backend.main:create_app --reload
   ```

2. Edit `frontend/src/App.tsx` and change:
   ```typescript
   const useMock = import.meta.env.DEV
   ```
   to:
   ```typescript
   const useMock = false
   ```

3. Refresh the browser

The UI will now connect to your backend via WebSocket and display real events.

### I want to customize the theme

Edit `frontend/tailwind.config.js` and change the color palette:

```javascript
colors: {
  critical: {
    500: '#ef4444',  // Change this red to your color
    // ...
  },
  // ...
}
```

Then restart the dev server (`npm run dev`).

### I want to change the layout

Edit `frontend/src/App.tsx` and modify the grid structure in the return statement:

```typescript
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
  {/* Change grid-cols-2 to grid-cols-3 for 3 columns, etc. */}
</div>
```

### I want to disable dark mode

Edit `frontend/tailwind.config.js`:

```javascript
darkMode: false,  // Disable dark mode
```

And remove the theme toggle from `frontend/src/components/Header.tsx`.

### I want to see real backend events

1. Backend must send events to WebSocket
2. Check `FRONTEND_INTEGRATION.md` for event schema
3. Use browser DevTools → Network → WS to see events
4. Check console for any errors

## Understanding the UI Layout

```
┌─────────────────────────────────────────┐
│  Header: Status + Theme Toggle          │
├──────────────┬──────────────────────────┤
│              │                          │
│   Agents     │   Execution Plan         │
│              │                          │
├──────────────┼──────────────────────────┤
│              │                          │
│   Thoughts   │   Findings               │
│              │                          │
├──────────────┴──────────────────────────┤
│                                         │
│       Tool Activity Log                 │
│                                         │
└─────────────────────────────────────────┘
```

Each panel:
- **Updates in real-time** from WebSocket events
- **Has auto-scrolling** to show new content
- **Is clickable** to expand/collapse details
- **Uses colors** to indicate severity/status

## File Organization

**You probably want to edit:**
- `src/App.tsx` - Main layout, mock events toggle
- `src/components/` - Panel designs
- `tailwind.config.js` - Colors, theme
- `src/hooks/useWebSocket.ts` - Backend connection

**You probably don't need to edit:**
- `src/store.ts` - State management (works as-is)
- `src/types.ts` - Event types (matches backend)
- `src/utils/` - Formatting helpers

## Debugging

### Check Connection Status
- Look at top right: green "Connected" or gray "Disconnected"
- If disconnected, check backend is running
- Open DevTools → Network → WS tab to see WebSocket messages

### Check for Errors
- Open DevTools → Console
- Any red errors? Let us know
- Yellow warnings are usually fine

### Check Event Format
- DevTools → Network → WS → Messages
- Each message should have: `event_type`, `agent_id`, `timestamp`, `event_id`, `data`
- See `FRONTEND_INTEGRATION.md` for expected format

### Check Component Updates
- DevTools → React DevTools tab
- Select a component, watch for re-renders
- Check the "Props" panel to see current state

## Performance Tips

If the UI feels slow:

1. **Too many events?** Edit `frontend/src/store.ts` and reduce max history:
   ```typescript
   const events = [...state.events, event].slice(-500)  // Was 1000
   ```

2. **Laggy animations?** Reduce animation count or duration in components

3. **Memory usage?** Check how many findings/events you're keeping

4. **Network slow?** Check WebSocket in DevTools → Network → WS

## Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| "Connected" never changes | Backend not running, check port 8000 |
| No events appearing | Check mock events are enabled, or backend sending events |
| UI looks wrong | Clear cache (Cmd+Shift+R), restart dev server |
| Dark mode not working | Check `dark` class is on `<html>` element |
| Animations stutter | Check browser performance, reduce animation count |

## Next Steps

1. **Explore the code** - Start with `App.tsx` to understand flow
2. **Read the docs** - Check `README.md`, `FRONTEND_DESIGN.md`, `FRONTEND_INTEGRATION.md`
3. **Customize it** - Change colors, layout, or add features
4. **Connect backend** - Point to real backend events
5. **Deploy** - Run `npm run build` and deploy to server

## Getting Help

- **Setup issues?** Check `README.md`
- **Design questions?** See `FRONTEND_DESIGN.md`
- **Backend integration?** Read `FRONTEND_INTEGRATION.md`
- **Still stuck?** Check the browser console for errors

## Want to Learn More?

- **React & Hooks**: [react.dev](https://react.dev)
- **Zustand**: [zustand.surge.sh](https://zustand.surge.sh)
- **Framer Motion**: [www.framer.com/motion](https://www.framer.com/motion)
- **Tailwind CSS**: [tailwindcss.com](https://tailwindcss.com)
- **TypeScript**: [typescriptlang.org](https://www.typescriptlang.org)

---

Happy coding! 🚀
