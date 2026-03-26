/**
 * Terminal Component - Console/terminal emulator for analysis logs
 * Minimal dark theme with semantic colors for different log types
 */

import { useStore } from "../store";
import { useEffect, useRef } from "react";
import { Trash2 } from "lucide-react";

interface TerminalProps {
  className?: string;
}

export function Terminal({ className = "" }: TerminalProps) {
  const { terminalLogs, clearTerminalLogs } = useStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollRef.current) {
      const timer = setTimeout(() => {
        if (scrollRef.current) {
          scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [terminalLogs]);

  // Determine log type and styling
  const getLogStyle = (log: string) => {
    if (log.includes("Error") || log.includes("error") || log.includes("✗")) {
      return "text-critical-500";
    }
    if (
      log.includes("Warning") ||
      log.includes("warning") ||
      log.includes("⚠")
    ) {
      return "text-warning-500";
    }
    if (
      log.includes("✓") ||
      log.includes("complete") ||
      log.includes("Complete")
    ) {
      return "text-success-500";
    }
    return "text-code-text";
  };

  return (
    <div
      className={`flex flex-col h-full bg-code-bg border-t border-code-border ${className}`}
    >
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-5 py-2.5 bg-code-bg-subtle border-b border-code-border flex-shrink-0">
        <span className="text-xs font-semibold text-code-text-secondary">
          Terminal
        </span>
        <div className="flex items-center gap-2">
          <span className="text-xs text-code-text-muted">
            {terminalLogs.length}
          </span>
          <button
            onClick={clearTerminalLogs}
            title="Clear terminal"
            className="text-code-text-muted hover:text-code-accent transition-colors p-1.5 rounded
                       hover:bg-code-surface focus:outline-none focus:ring-1 focus:ring-code-accent"
          >
            <Trash2 size={14} strokeWidth={1.5} />
          </button>
        </div>
      </div>

      {/* Terminal Output */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto font-mono text-xs p-4 space-y-1.5 bg-code-bg"
        role="log"
        aria-live="polite"
        aria-label="Terminal output"
      >
        {terminalLogs.length === 0 ? (
          <div className="text-code-text-muted space-y-1">
            <p className="text-code-accent">$ Ready for code analysis...</p>
            <p className="text-code-text-muted text-opacity-70">
              Upload or write code to begin
            </p>
          </div>
        ) : (
          terminalLogs.map((log, idx) => (
            <div
              key={idx}
              className={`${getLogStyle(log)} whitespace-pre-wrap break-words leading-6`}
            >
              {log}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
