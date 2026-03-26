/**
 * Type definitions for the streaming UI
 * Matches backend event schema from models.py
 */

export type EventType =
  | "agent_started"
  | "agent_completed"
  | "agent_error"
  | "thinking"
  | "tool_call_start"
  | "tool_call_result"
  | "finding_discovered"
  | "findings_consolidated"
  | "plan_created"
  | "agent_delegated"
  | "final_report"
  | "fix_proposed"
  | "fix_verified";

export type AgentType = "coordinator" | "security_agent" | "bug_agent";

export type AgentStatus =
  | "idle"
  | "thinking"
  | "tool_calling"
  | "completed"
  | "error";

export type Severity = "critical" | "high" | "medium" | "low" | "info";

export interface StreamEvent {
  event_type: EventType;
  agent_id: AgentType;
  timestamp: string;
  event_id: string;
  data: Record<string, any>;
}

export interface AgentState {
  id: AgentType;
  name: string;
  status: AgentStatus;
  startTime?: number;
  endTime?: number;
}

export interface Finding {
  id: string;
  agent_id: AgentType;
  severity: Severity;
  category: string;
  line?: number;
  description: string;
  details?: string;
  proposedFix?: string;
  fixVerified?: boolean;
}

export interface ToolCall {
  id: string;
  agent_id: AgentType;
  tool_name: string;
  input: Record<string, any>;
  output?: Record<string, any>;
  duration_ms?: number;
  timestamp: string;
}

export interface PlanStep {
  id: number;
  description: string;
  status: "pending" | "in_progress" | "completed";
}

export interface ThoughtStreamEntry {
  id: string;
  agent_id: AgentType;
  content: string;
  timestamp: string;
}
