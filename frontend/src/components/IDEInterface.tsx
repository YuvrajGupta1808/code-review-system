/**
 * Main IDE Interface - Professional layout with code editor, terminal, and results panel
 * Minimal dark theme inspired by Cursor and VS Code
 */

import { IDEToolbar } from "./IDEToolbar";
import { CodeEditor } from "./CodeEditor";
import { Terminal } from "./Terminal";
import { ResultsPanel } from "./ResultsPanel";
import { SplitPane } from "./SplitPane";
import { useStore } from "../store";

export function IDEInterface() {
  const { clearTerminalLogs, setCodeContent } = useStore();

  const handleReset = () => {
    setCodeContent("");
    clearTerminalLogs();
  };

  return (
    <div className="flex flex-col h-screen bg-code-bg">
      {/* Toolbar */}
      <IDEToolbar onReset={handleReset} />

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden flex">
        {/* Left: Code Editor + Terminal */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <SplitPane
            orientation="vertical"
            defaultSize={60}
            minSize={30}
            maxSize={80}
          >
            {/* Code Editor */}
            <div className="overflow-hidden">
              <CodeEditor />
            </div>

            {/* Terminal */}
            <div className="overflow-hidden">
              <Terminal />
            </div>
          </SplitPane>
        </div>

        {/* Right: Results Panel */}
        <div className="w-96 overflow-hidden border-l border-code-border">
          <ResultsPanel />
        </div>
      </div>
    </div>
  );
}
