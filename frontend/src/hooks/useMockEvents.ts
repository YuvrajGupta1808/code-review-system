/**
 * Hook for generating mock events (useful for development/demo)
 */

import { useEffect } from "react";
import { useStore } from "../store";
import type { AgentType } from "../types";

const mockFindings = [
  {
    finding_id: "sqli_001",
    severity: "critical" as const,
    category: "sql_injection",
    description: "SQL Injection vulnerability detected",
    details:
      "User input directly concatenated into SQL query without parameterization",
    line: 45,
    proposed_fix: `query = 'SELECT * FROM users WHERE id = ?'
cursor.execute(query, (user_id,))`,
  },
  {
    finding_id: "none_ref_001",
    severity: "high" as const,
    category: "null_reference",
    description: "Potential None reference",
    details: "Variable 'user' may be None when accessed",
    line: 23,
  },
  {
    finding_id: "hardcoded_key",
    severity: "critical" as const,
    category: "hardcoded_secret",
    description: "Hardcoded API key found",
    details: "API key exposed in source code (line 12)",
    line: 12,
  },
  {
    finding_id: "xss_001",
    severity: "high" as const,
    category: "xss",
    description: "Potential XSS vulnerability",
    details: "User input rendered without escaping",
    line: 67,
  },
  {
    finding_id: "race_cond",
    severity: "medium" as const,
    category: "race_condition",
    description: "Possible race condition",
    details: "Shared resource accessed without synchronization",
    line: 89,
  },
];

const mockThoughts = [
  "Analyzing the code structure...",
  "I notice this file handles database queries",
  "Let me examine the query construction method",
  "I see string concatenation being used for SQL queries",
  "This is a classic SQL injection pattern",
  "The user input flows directly into the query",
  "No parameterization or prepared statements are used",
  "This is a critical security issue",
];

export function useMockEvents(enabled: boolean = false) {
  const store = useStore();

  useEffect(() => {
    if (!enabled) return;

    // Simulate a review session
    const events: Array<{ delay: number; fn: () => void }> = [];

    // Coordinator starts
    events.push({
      delay: 500,
      fn: () => {
        store.updateAgentStatus("coordinator", "thinking");
        store.addEvent({
          event_type: "agent_started",
          agent_id: "coordinator",
          timestamp: new Date().toISOString(),
          event_id: "evt_coord_start",
          data: { message: "Starting code review analysis" },
        });
      },
    });

    // Plan created
    events.push({
      delay: 1500,
      fn: () => {
        store.addEvent({
          event_type: "plan_created",
          agent_id: "coordinator",
          timestamp: new Date().toISOString(),
          event_id: "evt_plan",
          data: {
            steps: [
              "Parse code structure",
              "Security analysis",
              "Bug detection",
              "Consolidate findings",
              "Generate fixes",
              "Final report",
            ],
          },
        });
        store.setPlan([
          { id: 1, description: "Parse code structure", status: "completed" },
          { id: 2, description: "Security analysis", status: "in_progress" },
          { id: 3, description: "Bug detection", status: "pending" },
          { id: 4, description: "Consolidate findings", status: "pending" },
          { id: 5, description: "Generate fixes", status: "pending" },
          { id: 6, description: "Final report", status: "pending" },
        ]);
      },
    });

    // Security agent starts
    events.push({
      delay: 2000,
      fn: () => {
        store.updateAgentStatus("security_agent", "thinking");
        store.addEvent({
          event_type: "agent_started",
          agent_id: "security_agent",
          timestamp: new Date().toISOString(),
          event_id: "evt_sec_start",
          data: { message: "Starting security analysis" },
        });
      },
    });

    // Streaming thoughts from security agent
    mockThoughts.forEach((thought, idx) => {
      events.push({
        delay: 2200 + idx * 300,
        fn: () => {
          store.addEvent({
            event_type: "thinking",
            agent_id: "security_agent",
            timestamp: new Date().toISOString(),
            event_id: `evt_thought_${idx}`,
            data: { content: thought },
          });
          store.addThought({
            id: `thought_${idx}`,
            agent_id: "security_agent",
            content: thought,
            timestamp: new Date().toISOString(),
          });
        },
      });
    });

    // Tool calls
    events.push({
      delay: 4500,
      fn: () => {
        store.addEvent({
          event_type: "tool_call_start",
          agent_id: "security_agent",
          timestamp: new Date().toISOString(),
          event_id: "evt_tool_start",
          data: {
            tool_name: "code_scanner",
            input: { file: "main.py", patterns: ["sql", "xss"] },
          },
        });
      },
    });

    events.push({
      delay: 5000,
      fn: () => {
        store.addEvent({
          event_type: "tool_call_result",
          agent_id: "security_agent",
          timestamp: new Date().toISOString(),
          event_id: "evt_tool_result",
          data: {
            tool_name: "code_scanner",
            output: {
              issues: 3,
              vulnerabilities: ["sql_injection", "hardcoded_secret"],
            },
            duration_ms: 234,
          },
        });
      },
    });

    // Findings
    mockFindings.forEach((finding, idx) => {
      events.push({
        delay: 5200 + idx * 400,
        fn: () => {
          const agentId: AgentType = idx < 3 ? "security_agent" : "bug_agent";
          store.updateAgentStatus(agentId, "thinking");
          store.addEvent({
            event_type: "finding_discovered",
            agent_id: agentId,
            timestamp: new Date().toISOString(),
            event_id: `evt_finding_${idx}`,
            data: finding,
          });
          store.addFinding({
            id: finding.finding_id,
            agent_id: agentId,
            severity: finding.severity,
            category: finding.category,
            line: finding.line,
            description: finding.description,
            details: finding.details,
          });
        },
      });
    });

    // Fix proposed
    events.push({
      delay: 7000,
      fn: () => {
        store.addEvent({
          event_type: "fix_proposed",
          agent_id: "security_agent",
          timestamp: new Date().toISOString(),
          event_id: "evt_fix_proposal",
          data: {
            finding_id: "sqli_001",
            proposed_fix: mockFindings[0].proposed_fix,
            explanation: "Use parameterized queries to prevent SQL injection",
            confidence: 0.95,
          },
        });
      },
    });

    // Bug agent starts
    events.push({
      delay: 7200,
      fn: () => {
        store.updateAgentStatus("bug_agent", "thinking");
        store.updatePlanStep(2, "completed");
        store.updatePlanStep(3, "in_progress");
      },
    });

    // Completion
    events.push({
      delay: 8500,
      fn: () => {
        store.updateAgentStatus("security_agent", "completed");
        store.updateAgentStatus("bug_agent", "completed");
        store.updatePlanStep(3, "completed");
        store.updatePlanStep(4, "completed");
        store.addEvent({
          event_type: "final_report",
          agent_id: "coordinator",
          timestamp: new Date().toISOString(),
          event_id: "evt_final",
          data: {
            total_findings: 5,
            critical: 2,
            high: 2,
            medium: 1,
          },
        });
      },
    });

    // Schedule all events
    const timeouts = events.map((event) => setTimeout(event.fn, event.delay));

    return () => {
      timeouts.forEach(clearTimeout);
    };
  }, [enabled, store]);
}
