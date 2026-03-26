/**
 * Zustand store for managing UI state and streaming events
 */

import { create } from "zustand";
import type {
  StreamEvent,
  AgentState,
  Finding,
  ToolCall,
  PlanStep,
  ThoughtStreamEntry,
  AgentStatus,
  AgentType,
} from "./types";

interface ReviewStore {
  // Agent state
  agents: Map<AgentType, AgentState>;
  updateAgentStatus: (agentId: AgentType, status: AgentStatus) => void;

  // Events
  events: StreamEvent[];
  addEvent: (event: StreamEvent) => void;
  clearEvents: () => void;

  // Findings
  findings: Finding[];
  addFinding: (finding: Finding) => void;
  updateFinding: (findingId: string, partial: Partial<Finding>) => void;

  // Tool calls
  toolCalls: ToolCall[];
  addToolCall: (toolCall: ToolCall) => void;

  // Thoughts
  thoughts: ThoughtStreamEntry[];
  addThought: (thought: ThoughtStreamEntry) => void;

  // Plan
  plan: PlanStep[];
  setPlan: (plan: PlanStep[]) => void;
  updatePlanStep: (
    stepId: number,
    status: "pending" | "in_progress" | "completed",
  ) => void;

  // Session
  isConnected: boolean;
  setConnected: (connected: boolean) => void;
  currentReviewId?: string;
  setCurrentReviewId: (id: string) => void;

  // UI
  theme: "light" | "dark";
  toggleTheme: () => void;
  selectedFindingId?: string;
  setSelectedFindingId: (id?: string) => void;

  // IDE State
  uiMode: "home" | "editor";
  setUiMode: (mode: "home" | "editor") => void;
  codeContent: string;
  setCodeContent: (content: string) => void;
  fileName: string;
  setFileName: (name: string) => void;
  terminalLogs: string[];
  addTerminalLog: (log: string) => void;
  clearTerminalLogs: () => void;
}

export const useStore = create<ReviewStore>((set) => ({
  // Initial agent states
  agents: new Map([
    ["coordinator", { id: "coordinator", name: "Coordinator", status: "idle" }],
    [
      "security_agent",
      { id: "security_agent", name: "Security Agent", status: "idle" },
    ],
    [
      "bug_agent",
      { id: "bug_agent", name: "Bug Detection Agent", status: "idle" },
    ],
  ]),

  updateAgentStatus: (agentId, status) =>
    set((state) => {
      const agents = new Map(state.agents);
      const agent = agents.get(agentId);
      if (agent) {
        const startTime = agent.startTime;
        const newStartTime =
          status === "thinking" || status === "tool_calling"
            ? Date.now()
            : startTime;
        const newEndTime =
          status === "completed" || status === "error"
            ? Date.now()
            : agent.endTime;
        agents.set(agentId, {
          ...agent,
          status,
          startTime: newStartTime,
          endTime: newEndTime,
        });
      }
      return { agents };
    }),

  events: [],
  addEvent: (event) =>
    set((state) => {
      // Keep last 1000 events in memory
      const events = [...state.events, event].slice(-1000);
      return { events };
    }),
  clearEvents: () => set({ events: [] }),

  findings: [],
  addFinding: (finding) =>
    set((state) => ({
      findings: [...state.findings, finding],
    })),
  updateFinding: (findingId, partial) =>
    set((state) => ({
      findings: state.findings.map((f) =>
        f.id === findingId ? { ...f, ...partial } : f,
      ),
    })),

  toolCalls: [],
  addToolCall: (toolCall) =>
    set((state) => {
      // Keep last 500 tool calls
      const toolCalls = [...state.toolCalls, toolCall].slice(-500);
      return { toolCalls };
    }),

  thoughts: [],
  addThought: (thought) =>
    set((state) => {
      // Keep last 200 thoughts
      const thoughts = [...state.thoughts, thought].slice(-200);
      return { thoughts };
    }),

  plan: [],
  setPlan: (plan) => set({ plan }),
  updatePlanStep: (stepId, status) =>
    set((state) => ({
      plan: state.plan.map((step) =>
        step.id === stepId ? { ...step, status } : step,
      ),
    })),

  isConnected: false,
  setConnected: (connected) => set({ isConnected: connected }),
  setCurrentReviewId: (id) => set({ currentReviewId: id }),

  theme: "dark",
  toggleTheme: () =>
    set((state) => {
      const newTheme = state.theme === "light" ? "dark" : "light";
      // Apply to document
      if (newTheme === "dark") {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
      return { theme: newTheme };
    }),

  setSelectedFindingId: (id) => set({ selectedFindingId: id }),

  // IDE State
  uiMode: "home",
  setUiMode: (mode) => set({ uiMode: mode }),
  codeContent: "",
  setCodeContent: (content) => set({ codeContent: content }),
  fileName: "untitled.js",
  setFileName: (name) => set({ fileName: name }),
  terminalLogs: [],
  addTerminalLog: (log) =>
    set((state) => {
      const terminalLogs = [...state.terminalLogs, log].slice(-100);
      return { terminalLogs };
    }),
  clearTerminalLogs: () => set({ terminalLogs: [] }),
}));
