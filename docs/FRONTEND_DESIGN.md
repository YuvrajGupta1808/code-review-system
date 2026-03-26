# Frontend Design Document

## Overview

The Code Review System UI is a professional, modern streaming interface for visualizing real-time multi-agent code analysis. It combines current web design trends with functional UX patterns optimized for technical users.

## Design Philosophy

### Principles
1. **Real-Time Focus** - Prioritize live feedback and immediate visual feedback
2. **Information Hierarchy** - Most critical info (agent status, findings) at top
3. **Dark-First Design** - Professional dark theme with optional light mode
4. **Minimal Decorative Elements** - Form follows function
5. **Clear Visual Feedback** - Status changes are obvious and satisfying
6. **Accessible Defaults** - WCAG 2.1 AA compliance built-in

### Target User
Technical users (developers, security engineers) analyzing code for vulnerabilities and bugs. Familiar with terminals, logs, and technical output. Value clarity and actionability over aesthetics.

## Visual Design System

### Color Palette

**Primary**
- Blue-500: Primary actions, active states, informational content
- Blue-600: Hover states

**Semantic Colors**
- Critical (Red): `#ef4444` - Security vulnerabilities, critical issues
- High (Orange): `#f97316` - High-priority issues
- Medium (Yellow/Amber): `#eab308` - Medium-priority items
- Low (Blue): `#0ea5e9` - Low-priority items
- Success (Green): `#22c55e` - Completed, verified, positive actions

**Neutrals**
- Gray-50-100: Light backgrounds
- Gray-900-950: Dark backgrounds
- Gray-600-700: Secondary text

### Typography

**Font Stack**: System fonts (sans-serif)
- Headlines: 18px (lg), 16px (base)
- Body: 14px
- Monospace: 12px (for code/logs)
- Font Weight: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Spacing
- Base unit: 4px
- Components: 8px (xs), 12px (sm), 16px (md), 24px (lg), 32px (xl)
- Padding: 6px (tight), 12px (normal), 16px (relaxed), 24px (spacious)

### Shadows & Borders
- Borders: 1px solid (subtle, for separation)
- Border radius: 8px (standard), 12px (cards)
- Shadows: Subtle (development only, card elevation)

## Layout System

### Grid Architecture
```
┌─────────────────────────────────────────────┐
│         Header (sticky, full width)         │
├─────────────────────────────────────────────┤
│                                             │
│  ┌────────────────┬──────────────────────┐ │
│  │                │                      │ │
│  │  Agent Status  │ Execution Plan       │ │  Main 2x2 Grid
│  │                │                      │ │
│  └────────────────┼──────────────────────┘ │
│                   │                        │
│  ┌────────────────┼──────────────────────┐ │
│  │                │                      │ │
│  │  Live Thoughts │ Findings Feed        │ │
│  │                │                      │ │
│  └────────────────┴──────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │       Tool Activity (Full Width)    │   │  Activity Log
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘

Breakpoints:
- Mobile: < 768px (single column)
- Tablet: 768px - 1024px (2-column)
- Desktop: > 1024px (optimized 2x2 + full width)
```

### Panel Characteristics

**Agent Status Panel**
- Purpose: Quick overview of system state
- Content: 3 agent cards with status badges
- Height: Flexible (minimal)
- Update Frequency: Real-time (< 100ms)
- Interactions: Hover for emphasis

**Execution Plan Panel**
- Purpose: Show workflow progress
- Content: 5-6 step list with status
- Height: Flexible (minimal)
- Update Frequency: As tasks progress (~500ms)
- Interactions: Visual progress indicators

**Live Thoughts Panel**
- Purpose: Understand agent reasoning
- Content: Streaming text from current agent
- Height: Fixed (400px)
- Update Frequency: Real-time (< 100ms)
- Interactions: Auto-scroll, scrollable history
- Behavior: Shows 5 most recent thoughts

**Findings Feed Panel**
- Purpose: Identify issues
- Content: Expanding cards with details
- Height: Fixed (400px)
- Update Frequency: As issues discovered (~2-5s)
- Interactions: Click to expand, view details/fixes
- Sorting: By severity (critical → low)

**Tool Activity Panel**
- Purpose: Audit tool usage
- Content: Tool call logs with timing
- Height: Fixed (400px)
- Update Frequency: As tools invoke (< 500ms)
- Interactions: Scrollable history, syntax highlighting
- Behavior: Shows 8 most recent calls

## Interaction Design

### Agent Status Changes
```
idle ──────────────> thinking/tool_calling ──────────> completed
[gray, static]       [blue/amber, pulsing]              [green, static]
                                          └──────────> error
                                              [red, static]
```

**Visual Feedback**
- Pulse animation: 2s cycle for active states
- Color transition: Instant
- Icon change: Instant with scale-in animation
- Duration: 200-300ms transitions

### Finding Discovery
**Animation Sequence**
1. Slide in from bottom (300ms ease-out)
2. Highlight background for 1s
3. Return to normal opacity
4. Expandable on click (200ms height animation)

**Expanded State**
- Shows: Details, proposed fix, verification status
- Styling: Darker background to emphasize detail view
- Border: Thicker border on left side for visual weight

### Thought Streaming
**Text Animation**
- Fade in on arrival (200ms)
- Cursor animation (█ blinks) on latest thought
- Monospace font for code references
- Line-height: 1.5 for readability

### Tool Call Display
```
[Time] [Agent] tool_name
  Input: {...}
  Output: {...}
  Duration: Xms
```

**Syntax Highlighting**
- Dark background (gray-100/900)
- Subtle text colors
- Monospace font (12px)
- Horizontal scroll for long JSON

## Animations & Transitions

### Duration Guidelines
- **Instant**: 0ms (state changes, immediate feedback)
- **Quick**: 200ms (panel animations, theme toggle)
- **Normal**: 300ms (sliding, fade, height changes)
- **Slow**: 500-1000ms (entrance animations, complex sequences)

### Easing Functions
- **ease-out**: Entrance animations (decelerate)
- **ease-in**: Exit animations (accelerate)
- **ease-in-out**: Bidirectional (scrolling, expand/collapse)
- **linear**: Continuous motion (spinning loaders, progress)

### Specific Animations

| Element | Animation | Duration | Easing | Repeat |
|---------|-----------|----------|--------|--------|
| Agent status dot | scale pulse | 2s | ease-in-out | ∞ |
| Agent status badge | opacity pulse | 1s | ease-in-out | ∞ |
| Loader icon | rotate | 2s | linear | ∞ |
| Finding card | slideUp + fadeIn | 300ms | ease-out | Once |
| Finding expand | height animate | 200ms | ease-in-out | Once |
| Thought entry | fadeIn | 300ms | ease-in | Once |
| Theme transition | all | 200ms | ease-out | Once |

## Responsive Behavior

### Mobile (< 768px)
- Single column layout
- Panels stack vertically
- Panel heights reduced to 300px
- Font sizes reduced (14px → 12px)
- Padding reduced (16px → 12px)
- No hover states (use tap)

### Tablet (768px - 1024px)
- 2-column layout
- 2x2 grid on tablet
- Activity log takes full width
- Panel heights 350px
- Normal spacing

### Desktop (> 1024px)
- 2x2 grid + full-width activity log
- Panel heights 400px
- Hover states active
- Maximum content width: 1280px

### Orientation Changes
- Auto-adjust grid when orientation changes
- Smooth layout transition (300ms)
- Maintain scroll position

## Dark Mode Implementation

### Approach: CSS Class
- Root element: `<html class="dark">`
- Tailwind prefix: `dark:`
- Color mapping: Automatic via Tailwind

### Theme Toggle Flow
1. Click theme button
2. Update Zustand store
3. Apply/remove `dark` class to `<html>`
4. Tailwind styles auto-apply
5. Transition: 200ms for all color changes

### Color Adjustments by Component

| Component | Light | Dark |
|-----------|-------|------|
| Background | white (#fff) | gray-900 (#111) |
| Surface | gray-50 (#f9f) | gray-800 (#1f2) |
| Border | gray-200 (#e5e) | gray-800 (#1f2) |
| Text Primary | gray-900 (#111) | white (#fff) |
| Text Secondary | gray-600 (#666) | gray-400 (#999) |

## Accessibility

### WCAG 2.1 AA Compliance

**Contrast Ratios**
- Large text (18px+): 3:1 minimum
- Normal text: 4.5:1 minimum
- Graphics: 3:1 minimum
- Current: All ≥ 4.5:1

**Color Independence**
- Status not conveyed by color alone
- Supporting text/icon always present
- Critical info uses shape + color

**Keyboard Navigation**
- All interactive elements focusable
- Focus indicators visible (2px border)
- Tab order logical (top-to-bottom, left-to-right)
- Escape closes modals/menus

**Screen Readers**
- Semantic HTML (buttons, headings, lists)
- ARIA labels where needed
- Live region updates for real-time data
- Form labels associated

**Motion**
- Respects `prefers-reduced-motion`
- No auto-playing animations on load
- Animations < 3 seconds by default

## Performance Targets

### Load Time
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Time to Interactive: < 3.5s
- Cumulative Layout Shift: < 0.1

### Runtime
- Frame rate: 60 FPS minimum
- Event processing: < 5ms per event
- Theme toggle: < 100ms
- Scroll smoothness: 60 FPS maintained

### Bundle Size
- Main bundle: < 200KB (gzip)
- CSS: < 50KB
- JavaScript: < 150KB
- Initial load: < 50 requests

## Design System Components

### Card Container
```tsx
<div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
  {/* content */}
</div>
```

### Status Badge
```tsx
<div className={clsx(
  'px-3 py-1 rounded text-xs font-semibold text-white',
  { 'bg-blue-500': active, 'bg-gray-400': inactive }
)}>
  ACTIVE
</div>
```

### Icon + Text Pair
```tsx
<div className="flex items-center gap-2">
  <IconComponent className="w-4 h-4" />
  <span className="text-sm font-medium">Label</span>
</div>
```

## Future Design Considerations

### Phase 2
- Code diff viewer for proposed fixes
- Line-by-line findings mapping
- Custom agent configuration panel
- Real-time metrics/performance dashboard

### Phase 3
- Collaborative annotations
- Findings timeline/history
- Advanced filtering UI
- PDF report generation

## Design Decisions & Rationale

### Why Dark Theme First?
- Reduces eye strain during extended use (common for developers)
- Professional appearance for technical tools
- Better visual hierarchy with accent colors
- Preferred by majority of developers (surveys)

### Why 2x2 + Full Width Layout?
- Balances agent status (must see) with findings (must track)
- Tool logs less frequently accessed, full width reduces clutter
- Responsive single-column on mobile
- Natural workflow: status → findings → deep dive

### Why Framer Motion?
- Declarative animation syntax
- Performance-optimized (GPU acceleration)
- Small bundle size (58KB)
- Rich documentation and community

### Why Zustand?
- Minimal boilerplate
- DevTools integration
- Easy to understand and debug
- Scales from small to large apps

---

**Document Version**: 1.0
**Last Updated**: 2026-03-25
**Author**: Claude Code UI/UX Team
