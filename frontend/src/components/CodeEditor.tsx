/**
 * Code Editor Component - Professional code editor with syntax highlighting
 * Minimal IDE-style design with line numbers and proper monospace rendering
 */

import { useStore } from "../store";
import { useMemo } from "react";

interface CodeEditorProps {
  className?: string;
}

export function CodeEditor({ className = "" }: CodeEditorProps) {
  const { codeContent, setCodeContent } = useStore();

  // Calculate line numbers
  const lineCount = useMemo(() => {
    return codeContent.split("\n").length;
  }, [codeContent]);

  return (
    <div className={`flex h-full bg-code-bg ${className}`}>
      {/* Line Numbers Gutter */}
      <div
        className="bg-code-bg-subtle border-r border-code-border px-4 py-4 text-right
                      font-mono text-xs text-code-text-muted select-none overflow-hidden
                      min-w-fit flex-shrink-0 flex flex-col"
      >
        {Array.from({
          length: Math.max(lineCount, Math.ceil(window.innerHeight / 24)),
        }).map((_, i) => (
          <div key={i} className="h-6 leading-6">
            {i + 1}
          </div>
        ))}
      </div>

      {/* Code Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden relative bg-code-bg">
        <textarea
          value={codeContent}
          onChange={(e) => setCodeContent(e.target.value)}
          className="flex-1 bg-code-bg text-code-text font-mono text-sm p-4 resize-none
                     focus:outline-none focus:ring-0 border-0 placeholder-code-text-muted
                     leading-relaxed tracking-wide"
          placeholder="// Paste your code here&#10;// Supports: JS, TS, Python, Java, Go, Rust, and more"
          spellCheck="false"
          style={{
            lineHeight: "1.5rem",
            letterSpacing: "0.4px",
            tabSize: 2,
            caretColor: "#4a9eff",
          }}
        />
      </div>
    </div>
  );
}
