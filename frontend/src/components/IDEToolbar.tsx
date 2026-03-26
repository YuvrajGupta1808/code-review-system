/**
 * IDE Toolbar - Top toolbar with file info, status, and controls
 * Minimal dark theme with blue accents for actions
 */

import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";
import { Play, Square, RotateCcw, Sun, Moon, LogOut } from "lucide-react";
import clsx from "clsx";
import type { AgentType, StreamEvent } from "../types";

interface IDEToolbarProps {
  onRun?: () => void;
  onStop?: () => void;
  onReset?: () => void;
}

export function IDEToolbar({ onRun, onStop, onReset }: IDEToolbarProps) {
  const {
    fileName,
    codeContent,
    isConnected,
    theme,
    toggleTheme,
    setUiMode,
    addTerminalLog,
    setConnected,
    updateAgentStatus,
    addEvent,
    addThought,
    addFinding,
    updateFinding,
    addToolCall,
    setPlan,
    updatePlanStep,
  } = useStore();
  const [isRunning, setIsRunning] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Best-effort cleanup if the user navigates away mid-stream.
  useEffect(() => {
    return () => {
      eventSourceRef.current?.close();
      eventSourceRef.current = null;
    };
  }, []);

  const handleStop = () => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    setConnected(false);
    setIsRunning(false);
    onStop?.();
    addTerminalLog("✓ Stopped analysis");
  };

  const handleRun = async () => {
    const hasCode = codeContent.trim().length > 0;

    if (!hasCode) {
      addTerminalLog("✗ Error: No code to analyze (connecting to SSE anyway)");
    }

    // If something is already running, stop it first.
    if (eventSourceRef.current) {
      handleStop();
    }

    if (hasCode) {
      setIsRunning(true);
    }
    addTerminalLog(`$ Analyzing: ${fileName}`);
    addTerminalLog("Starting code review...");
    onRun?.();

    // SSE endpoint: backend will start the coordinator when it sees `?code=...`.
    const url = `http://localhost:8000/stream/review?code=${encodeURIComponent(codeContent)}`;

    const handleStreamEvent = (streamEvent: StreamEvent) => {
      addEvent(streamEvent);
      addTerminalLog(`[${streamEvent.event_type}]`);

      // Update agent status badges.
      if (
        streamEvent.event_type === "agent_started" ||
        streamEvent.event_type === "thinking"
      ) {
        updateAgentStatus(streamEvent.agent_id as AgentType, "thinking");
      } else if (streamEvent.event_type === "tool_call_start") {
        updateAgentStatus(streamEvent.agent_id as AgentType, "tool_calling");
      } else if (streamEvent.event_type === "agent_completed") {
        updateAgentStatus(streamEvent.agent_id as AgentType, "completed");
      } else if (streamEvent.event_type === "agent_error") {
        updateAgentStatus(streamEvent.agent_id as AgentType, "error");
      }

      if (streamEvent.event_type === "thinking") {
        addThought({
          id: streamEvent.event_id,
          agent_id: streamEvent.agent_id,
          content: streamEvent.data.content || "",
          timestamp: streamEvent.timestamp,
        });
      }

      if (streamEvent.event_type === "tool_call_start") {
        addToolCall({
          id: streamEvent.event_id,
          agent_id: streamEvent.agent_id,
          tool_name: streamEvent.data.tool_name || "",
          input: streamEvent.data.input || {},
          timestamp: streamEvent.timestamp,
        });
      }

      if (streamEvent.event_type === "tool_call_result") {
        addToolCall({
          id: streamEvent.event_id,
          agent_id: streamEvent.agent_id,
          tool_name: streamEvent.data.tool_name || "",
          input: streamEvent.data.input || {},
          output: streamEvent.data.output,
          duration_ms: streamEvent.data.duration_ms,
          timestamp: streamEvent.timestamp,
        });
      }

      if (streamEvent.event_type === "finding_discovered") {
        addFinding({
          id: streamEvent.data.finding_id || streamEvent.event_id,
          agent_id: streamEvent.agent_id,
          severity: streamEvent.data.severity || "info",
          category: streamEvent.data.category || "unknown",
          line: streamEvent.data.line,
          description: streamEvent.data.description || "",
          details: streamEvent.data.details,
        });
      }

      if (streamEvent.event_type === "fix_proposed") {
        const findingId = streamEvent.data.finding_id;
        const explanation =
          streamEvent.data.explanation || streamEvent.data.description || "";
        const proposedFix = streamEvent.data.proposed_fix || "";

        const { findings } = useStore.getState() as any;
        const existing = Array.isArray(findings)
          ? findings.find((f: any) => f.id === findingId)
          : undefined;

        if (existing) {
          updateFinding(findingId, { proposedFix, description: explanation });
        } else {
          addFinding({
            id: findingId || streamEvent.event_id,
            agent_id: streamEvent.agent_id,
            severity: "info",
            category: "unknown",
            description: explanation,
            proposedFix,
          });
        }
      }

      if (streamEvent.event_type === "fix_verified") {
        updateFinding(streamEvent.data.finding_id, {
          fixVerified: streamEvent.data.verification_passed,
        });
      }

      if (streamEvent.event_type === "plan_created") {
        const rawSteps =
          streamEvent.data.plan_steps || streamEvent.data.steps || [];
        const mapped = Array.isArray(rawSteps)
          ? rawSteps.map((step: any, idx: number) => ({
              id: typeof step.step === "number" ? step.step : idx + 1,
              description: step.description || step.action || String(step),
              status: "pending" as const,
            }))
          : [];
        setPlan(mapped);
      }

      if (streamEvent.event_type === "agent_delegated") {
        const delegatedTo = (streamEvent.data.delegated_to || "") as string;
        const task = (streamEvent.data.task || "") as string;
        const delegatedHuman =
          delegatedTo
            .replace("_agent", "")
            .replace(/_/g, " ")
            .replace(/\b\w/g, (m: string) => m.toUpperCase()) || task;

        const { plan } = useStore.getState() as any;
        const step = Array.isArray(plan)
          ? plan.find((s: any) =>
              String(s.description || "")
                .toLowerCase()
                .includes(delegatedHuman.toLowerCase()),
            )
          : undefined;
        if (step) updatePlanStep(step.id, "in_progress");
      }

      if (
        streamEvent.event_type === "agent_completed" &&
        streamEvent.agent_id !== "coordinator"
      ) {
        const agentId = streamEvent.agent_id as string;
        const human =
          agentId
            .replace("_agent", "")
            .replace(/_/g, " ")
            .replace(/\b\w/g, (m: string) => m.toUpperCase()) || agentId;

        const { plan } = useStore.getState() as any;
        const step = Array.isArray(plan)
          ? plan.find((s: any) =>
              String(s.description || "")
                .toLowerCase()
                .includes(human.toLowerCase()),
            )
          : undefined;
        if (step) updatePlanStep(step.id, "completed");
      }

      if (streamEvent.event_type === "final_report") {
        addTerminalLog("✓ Analysis complete");
        const { plan } = useStore.getState() as any;
        if (Array.isArray(plan) && plan.length > 0) {
          updatePlanStep(plan[plan.length - 1].id, "completed");
        }
        handleStop();
      }
    };

    try {
      const es = new EventSource(url);
      eventSourceRef.current = es;

      es.onopen = () => {
        setConnected(true);
        addTerminalLog("✓ Connected to analysis server (SSE)");
        addTerminalLog("✓ Code submitted for analysis");
      };

      es.onmessage = (event) => {
        try {
          const streamEvent: StreamEvent = JSON.parse(event.data);
          handleStreamEvent(streamEvent);
        } catch (e) {
          addTerminalLog(
            `✗ Failed to parse SSE message: ${String(event.data).slice(0, 200)}`,
          );
        }
      };

      es.onerror = () => {
        setConnected(false);
        addTerminalLog("✗ SSE connection error");
        handleStop();
      };
    } catch (error) {
      setConnected(false);
      setIsRunning(false);
      addTerminalLog(
        `✗ Failed to start analysis: ${error instanceof Error ? error.message : "Unknown error"}`,
      );
    }
  };

  return (
    <div className="bg-code-bg-subtle border-b border-code-border px-5 py-2.5 flex items-center justify-between flex-shrink-0">
      {/* Left Section - File Info */}
      <div className="flex items-center gap-5 min-w-0">
        <div className="flex items-center gap-2.5 min-w-0">
          <span className="text-xs font-mono text-code-text-muted flex-shrink-0">
            file:
          </span>
          <span className="text-sm text-code-text font-medium truncate">
            {fileName}
          </span>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center gap-2 pl-5 border-l border-code-border flex-shrink-0">
          <div
            className={clsx("w-1.5 h-1.5 rounded-full", {
              "bg-success-500 animate-pulse-subtle": isConnected,
              "bg-critical-500": !isConnected,
            })}
          />
          <span className="text-xs text-code-text-muted">
            {isConnected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      {/* Center Section - Controls */}
      <div className="flex items-center gap-3 flex-shrink-0">
        <button
          onClick={handleRun}
          disabled={isRunning}
          className={clsx(
            "flex items-center gap-2 px-4 py-2 rounded font-medium transition-all text-sm",
            isRunning
              ? "bg-code-surface text-code-text-muted cursor-not-allowed"
              : "bg-code-accent hover:bg-code-accent-hover text-code-bg hover:shadow-lg",
          )}
          title="Start code analysis"
        >
          <Play size={15} strokeWidth={2} fill="currentColor" />
          Analyze
        </button>

        {isRunning && (
          <button
            onClick={handleStop}
            className="flex items-center gap-2 px-4 py-2 rounded font-medium text-sm
                       bg-critical-500 hover:bg-critical-600 text-white transition-all"
            title="Stop analysis"
          >
            <Square size={14} strokeWidth={2} />
            Stop
          </button>
        )}

        <button
          onClick={onReset}
          className="p-2 rounded text-code-text-secondary hover:text-code-text hover:bg-code-surface
                     transition-colors focus:outline-none focus:ring-1 focus:ring-code-accent"
          title="Clear editor and terminal"
        >
          <RotateCcw size={15} strokeWidth={1.5} />
        </button>
      </div>

      {/* Right Section - Theme & Navigation */}
      <div className="flex items-center gap-2 pl-5 border-l border-code-border flex-shrink-0">
        <button
          onClick={toggleTheme}
          className="p-2 rounded hover:bg-code-surface transition-colors
                     text-code-text-muted hover:text-code-accent focus:outline-none
                     focus:ring-1 focus:ring-code-accent"
          title="Toggle theme"
        >
          {theme === "dark" ? (
            <Sun size={15} strokeWidth={1.5} />
          ) : (
            <Moon size={15} strokeWidth={1.5} />
          )}
        </button>

        <button
          onClick={() => setUiMode("home")}
          className="flex items-center gap-2 px-3 py-2 rounded text-xs font-medium
                     text-code-text-muted hover:text-code-text hover:bg-code-surface
                     transition-colors focus:outline-none focus:ring-1 focus:ring-code-accent"
          title="Return to home screen"
        >
          <LogOut size={14} strokeWidth={1.5} />
          Home
        </button>
      </div>
    </div>
  );
}
