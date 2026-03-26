# Quick Start - IDE-Style Code Review UI

Get up and running with the new professional IDE interface in seconds.

## Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already installed)
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

## What You'll See

### 1. Home Screen (First Load)
- Professional landing page
- Two big buttons: "Upload File" and "Write Code"
- Beautiful dark theme with blue accents

### 2. Upload File
- Click the "Upload File" button
- Select any code file (.js, .py, .java, etc.)
- File automatically loads into editor
- Transitions to IDE interface

### 3. Write Code
- Click the "Write Code" button
- Empty editor opens, ready for input
- Paste or type your code
- Analyze whenever ready

## Using the IDE

### Main Screen Layout

```
Top: Toolbar (File name, Status, Analyze button, etc.)

Center-Left:
  - Code Editor (top 60%)
  - Terminal (bottom 40%)
  - Resizable divider in between

Right:
  - Results Panel (Findings, Logs, Events)
```

### Step-by-Step Analysis

1. **Get Code Into Editor**
   - Upload: Click "Upload File" → Select file
   - Write: Click "Write Code" → Type/paste code

2. **Start Analysis**
   - Click blue "Analyze" button in toolbar
   - Terminal shows: `$ Analyzing: filename.js`

3. **Watch Progress**
   - Terminal displays status updates
   - Results panel populates with findings

4. **Review Results**
   - **Findings Tab**: See all issues found
   - Click any finding to expand details
   - View suggested fixes
   - **Logs Tab**: See tool calls and durations
   - **Events Tab**: See system events

## Key Features

### Code Editor
- **Line Numbers**: Automatic column on left
- **Syntax Highlighting**: Colors for keywords, strings, comments
- **Full Code Support**: Any programming language
- **Auto-Save**: Changes tracked in real-time

### Terminal
- **Live Output**: See analysis progress
- **Auto-Scroll**: Jumps to bottom on new logs
- **Clear Button**: Wipe output when needed
- **Status Messages**: Clear feedback

### Results Panel

**Findings Tab:**
- 🔴 Critical issues in red
- 🟠 High severity in orange
- 🟡 Medium issues in yellow
- 🔵 Low issues in blue
- ⚪ Info in gray

**Expandable Details:**
- Description of the issue
- Line number where it occurs
- Technical details
- Suggested code fix

**Tool Logs Tab:**
- Every tool that ran
- How long it took
- Input parameters
- Output results

**Events Tab:**
- Chronological event stream
- Agent activity
- System messages

### Toolbar

| Feature | Usage |
|---------|-------|
| File Name | Shows current file (monospace) |
| 🟢 Status | Green = Connected, Red = Offline |
| ▶️ Analyze | Start code analysis |
| ⏹️ Stop | Halt running analysis |
| 🔄 Reset | Clear everything |
| 🌙 Theme | Toggle dark/light mode |
| 🏠 Home | Return to home screen |

## Common Tasks

### Upload a File

```
1. On home screen, click "Upload File"
2. Select file from computer
3. Click "Open"
4. Editor automatically fills with code
5. IDE interface opens
6. Ready to analyze!
```

### Paste Code Manually

```
1. Click "Write Code" button
2. Editor opens blank
3. Paste or type your code
4. Click "Analyze" to review
```

### View a Specific Finding

```
1. Look at Findings tab in right panel
2. Click any finding to expand
3. See category, severity, and line number
4. Read description and details
5. Review suggested fix code
```

### Check Tool Logs

```
1. Click "Logs" tab in Results panel
2. See list of all tools executed
3. Click any log to expand
4. View input parameters sent
5. View output data received
6. See execution duration
```

### Clear Everything

```
1. Click "🔄 Reset" button in toolbar
2. Code editor clears
3. Terminal output cleared
4. Results panel reset
5. Ready for new analysis
```

### Go Back to Home

```
1. Click "🏠 Home" button in toolbar
2. Returns to home screen
3. Can upload new file or write new code
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+A` / `Cmd+A` | Select all code |
| `Ctrl+C` / `Cmd+C` | Copy selected |
| `Ctrl+V` / `Cmd+V` | Paste code |
| `Ctrl+Z` / `Cmd+Z` | Undo (in editor) |
| `Tab` | Indent code (in editor) |

## Pro Tips

1. **Large Files**: The editor handles up to 1MB files. For larger codebases, upload smaller portions.

2. **Multi-Language**: The UI supports any programming language. Just upload and analyze!

3. **Resize Panels**: Drag the divider between editor and terminal to resize. Drag the results panel border to expand/collapse.

4. **Terminal Auto-Scroll**: New logs automatically scroll to view. Click "Scroll to bottom" if you manually scrolled up.

5. **Theme Toggle**: Click the moon/sun icon to switch between dark and light modes.

6. **Connection Status**: Green indicator means connected to backend. Red means disconnected (check your server).

## Troubleshooting

### "Upload File" Button Not Working
- Check browser console for errors
- Ensure file is valid text/code
- Try a smaller file
- Refresh page and try again

### Results Not Showing
- Check terminal for error messages
- Click "Analyze" button again
- Ensure backend is running
- Check connection status indicator

### Editor Shows Wrong Colors
- The basic syntax highlighting might be limited
- This is normal for non-standard languages
- Colors are functional, not perfect

### Terminal Output Very Long
- Click "Clear" button to wipe logs
- Click "Reset" to start fresh
- Terminal stores last 100 messages

### Resizing Not Working
- Try dragging from the middle of the divider line
- Look for cursor to change to resize icon
- Move mouse slowly while dragging

## Browser Compatibility

✅ Works great in:
- Chrome / Edge (version 90+)
- Firefox (version 88+)
- Safari (version 15+)

## Demo Mode

The system includes mock data for testing without a backend:
- Upload a file and click Analyze
- Simulated findings appear
- Terminal shows analysis progress
- Perfect for demo/testing

## Next Steps

1. **Explore the UI**: Click around, try uploading files
2. **Read the Docs**: Check IDE_UI_GUIDE.md for details
3. **Connect Backend**: Configure API endpoints when ready
4. **Customize**: Modify colors/styling in tailwind.config.js
5. **Extend**: Add new tabs or panels as needed

## Support

For detailed documentation, see:
- **IDE_UI_GUIDE.md** - Complete feature documentation
- **IMPLEMENTATION_SUMMARY.md** - Technical overview
- **Component code** - JSDoc comments in each file

---

**Happy Coding! 🚀**
