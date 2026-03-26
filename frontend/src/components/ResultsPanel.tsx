/**
 * Results Panel - Shows findings, tool logs, and events from agents
 * Minimal dark theme with semantic colors for different severity levels
 */

import { useStore } from "../store";
import {
  AlertCircle,
  CheckCircle,
  AlertTriangle,
  Info,
  ChevronDown,
} from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

interface ResultsPanelProps {
  className?: string;
}

const severityConfig = {
  critical: {
    icon: AlertCircle,
    color: "text-critical-500",
    bg: "bg-critical-500 bg-opacity-10",
    label: "Critical",
  },
  high: {
    icon: AlertCircle,
    color: "text-orange-400",
    bg: "bg-orange-400 bg-opacity-10",
    label: "High",
  },
  medium: {
    icon: AlertTriangle,
    color: "text-warning-500",
    bg: "bg-warning-500 bg-opacity-10",
    label: "Medium",
  },
  low: {
    icon: Info,
    color: "text-info-500",
    bg: "bg-info-500 bg-opacity-10",
    label: "Low",
  },
  info: {
    icon: Info,
    color: "text-code-text-secondary",
    bg: "bg-code-surface",
    label: "Info",
  },
};

export function ResultsPanel({ className = "" }: ResultsPanelProps) {
  const { findings, toolCalls, events } = useStore();
  const [activeTab, setActiveTab] = useState<"findings" | "logs" | "events">(
    "findings",
  );

  return (
    <div
      className={`flex flex-col h-full bg-code-bg border-l border-code-border ${className}`}
    >
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-code-border bg-code-bg-subtle flex-shrink-0">
        <h2 className="text-sm font-semibold text-code-text">
          Analysis Results
        </h2>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-code-border bg-code-bg flex-shrink-0">
        {(["findings", "logs", "events"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={clsx(
              "px-4 py-2.5 text-xs font-medium border-b-2 transition-colors",
              activeTab === tab
                ? "text-code-accent border-code-accent"
                : "text-code-text-muted border-transparent hover:text-code-text-secondary",
            )}
          >
            {tab === "findings" && `Findings (${findings.length})`}
            {tab === "logs" && `Logs (${toolCalls.length})`}
            {tab === "events" && `Events (${events.length})`}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto bg-code-bg">
        {activeTab === "findings" && <FindingsTab />}
        {activeTab === "logs" && <LogsTab />}
        {activeTab === "events" && <EventsTab />}
      </div>
    </div>
  );
}

function FindingsTab() {
  const { findings } = useStore();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (findings.length === 0) {
    return (
      <div className="p-4 text-sm text-code-text-muted text-center">
        <p>No findings yet</p>
        <p className="text-xs text-code-text-muted opacity-60 mt-1">
          Submit code to analyze for issues
        </p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-code-border">
      {findings.map((finding) => {
        const config = severityConfig[finding.severity];
        const Icon = config.icon;
        const isExpanded = expandedId === finding.id;

        return (
          <div key={finding.id} className="border-b border-code-border">
            <button
              onClick={() => setExpandedId(isExpanded ? null : finding.id)}
              className="w-full px-4 py-3 hover:bg-code-surface transition-colors text-left flex items-start gap-3"
            >
              <Icon
                className={clsx("w-4 h-4 mt-0.5 flex-shrink-0", config.color)}
                strokeWidth={2}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-semibold text-code-text">
                    {finding.category}
                  </span>
                  <span className={clsx("text-xs font-medium", config.color)}>
                    {config.label}
                  </span>
                  {finding.line !== undefined && (
                    <span className="text-xs text-code-text-muted">
                      Line {finding.line}
                    </span>
                  )}
                </div>
                <p className="text-sm text-code-text mt-1 leading-relaxed">
                  {finding.description}
                </p>
              </div>
              <ChevronDown
                size={16}
                strokeWidth={1.5}
                className={clsx(
                  "flex-shrink-0 text-code-text-muted transition-transform",
                  {
                    "rotate-180": isExpanded,
                  },
                )}
              />
            </button>

            {isExpanded && (
              <div className="px-4 py-3 bg-code-bg-subtle border-t border-code-border space-y-3">
                {finding.details && (
                  <div>
                    <h4 className="text-xs font-semibold text-code-text-secondary mb-1.5">
                      Details
                    </h4>
                    <p className="text-sm text-code-text-muted leading-relaxed">
                      {finding.details}
                    </p>
                  </div>
                )}

                {finding.proposedFix && (
                  <div>
                    <h4 className="text-xs font-semibold text-code-text-secondary mb-1.5">
                      Suggested Fix
                    </h4>
                    <pre
                      className="text-xs bg-code-bg p-2.5 rounded border border-code-border
                                    text-code-text-secondary overflow-x-auto font-mono leading-relaxed"
                    >
                      {finding.proposedFix}
                    </pre>
                  </div>
                )}

                {finding.fixVerified && (
                  <div className="flex items-center gap-2 text-xs text-success-500">
                    <CheckCircle size={14} strokeWidth={2} />
                    Fix verified
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function LogsTab() {
  const { toolCalls } = useStore();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (toolCalls.length === 0) {
    return (
      <div className="p-4 text-sm text-code-text-muted text-center">
        <p>No tool calls yet</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-code-border">
      {[...toolCalls].reverse().map((call) => {
        const isExpanded = expandedId === call.id;

        return (
          <div key={call.id} className="border-b border-code-border">
            <button
              onClick={() => setExpandedId(isExpanded ? null : call.id)}
              className="w-full px-4 py-3 hover:bg-code-surface transition-colors text-left flex items-start gap-3"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-mono bg-code-surface text-code-accent px-2 py-1 rounded">
                    {call.tool_name}
                  </span>
                  {call.duration_ms && (
                    <span className="text-xs text-code-text-muted">
                      {call.duration_ms}ms
                    </span>
                  )}
                </div>
                <p className="text-xs text-code-text-muted mt-1">
                  {new Date(call.timestamp).toLocaleTimeString()}
                </p>
              </div>
              <ChevronDown
                size={16}
                strokeWidth={1.5}
                className={clsx(
                  "flex-shrink-0 text-code-text-muted transition-transform",
                  {
                    "rotate-180": isExpanded,
                  },
                )}
              />
            </button>

            {isExpanded && (
              <div className="px-4 py-3 bg-code-bg-subtle border-t border-code-border space-y-2">
                {Object.keys(call.input).length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-code-text-secondary mb-1.5">
                      Input
                    </h4>
                    <pre
                      className="text-xs bg-code-bg p-2.5 rounded border border-code-border
                                    text-code-text-secondary overflow-x-auto font-mono leading-relaxed"
                    >
                      {JSON.stringify(call.input, null, 2)}
                    </pre>
                  </div>
                )}

                {call.output && Object.keys(call.output).length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-code-text-secondary mb-1.5">
                      Output
                    </h4>
                    <pre
                      className="text-xs bg-code-bg p-2.5 rounded border border-code-border
                                    text-code-text-secondary overflow-x-auto font-mono leading-relaxed"
                    >
                      {JSON.stringify(call.output, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function EventsTab() {
  const { events } = useStore();

  if (events.length === 0) {
    return (
      <div className="p-4 text-sm text-code-text-muted text-center">
        <p>No events yet</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-code-border text-xs">
      {[...events].reverse().map((event, idx) => (
        <div
          key={event.event_id || idx}
          className="px-4 py-2.5 hover:bg-code-surface transition-colors"
        >
          <div className="flex items-center gap-2">
            <span className="text-code-text-muted">
              {new Date(event.timestamp).toLocaleTimeString()}
            </span>
            <span className="text-code-accent font-mono text-xs">
              {event.agent_id}
            </span>
            <span className="text-code-text-secondary">{event.event_type}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
