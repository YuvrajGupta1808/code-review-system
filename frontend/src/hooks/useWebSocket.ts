/**
 * Custom hook for WebSocket connection and event handling
 */

import { useEffect, useRef, useCallback } from "react";
import { useStore } from "../store";
import type { StreamEvent, AgentType } from "../types";

export function useWebSocket(reviewId?: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const store = useStore();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const url = `${protocol}://${window.location.host}/ws/review${
      reviewId ? `?review_id=${reviewId}` : ""
    }`;

    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log("WebSocket connected");
        store.setConnected(true);
        reconnectAttemptsRef.current = 0;
      };

      wsRef.current.onmessage = (event) => {
        try {
          const streamEvent: StreamEvent = JSON.parse(event.data);
          store.addEvent(streamEvent);

          // Update agent status based on event type
          if (
            streamEvent.event_type === "agent_started" ||
            streamEvent.event_type === "thinking"
          ) {
            store.updateAgentStatus(
              streamEvent.agent_id as AgentType,
              "thinking",
            );
          } else if (streamEvent.event_type === "tool_call_start") {
            store.updateAgentStatus(
              streamEvent.agent_id as AgentType,
              "tool_calling",
            );
          } else if (streamEvent.event_type === "agent_completed") {
            store.updateAgentStatus(
              streamEvent.agent_id as AgentType,
              "completed",
            );
          } else if (streamEvent.event_type === "agent_error") {
            store.updateAgentStatus(streamEvent.agent_id as AgentType, "error");
          }

          // Handle specific event types
          if (streamEvent.event_type === "thinking") {
            store.addThought({
              id: streamEvent.event_id,
              agent_id: streamEvent.agent_id as AgentType,
              content: streamEvent.data.content || "",
              timestamp: streamEvent.timestamp,
            });
          }

          if (streamEvent.event_type === "tool_call_start") {
            store.addToolCall({
              id: streamEvent.event_id,
              agent_id: streamEvent.agent_id as AgentType,
              tool_name: streamEvent.data.tool_name || "",
              input: streamEvent.data.input || {},
              timestamp: streamEvent.timestamp,
            });
          }

          if (streamEvent.event_type === "tool_call_result") {
            store.addToolCall({
              id: streamEvent.event_id,
              agent_id: streamEvent.agent_id as AgentType,
              tool_name: streamEvent.data.tool_name || "",
              input: streamEvent.data.input || {},
              output: streamEvent.data.output,
              duration_ms: streamEvent.data.duration_ms,
              timestamp: streamEvent.timestamp,
            });
          }

          if (streamEvent.event_type === "finding_discovered") {
            store.addFinding({
              id: streamEvent.data.finding_id || streamEvent.event_id,
              agent_id: streamEvent.agent_id as AgentType,
              severity: streamEvent.data.severity || "info",
              category: streamEvent.data.category || "unknown",
              line: streamEvent.data.line,
              description: streamEvent.data.description || "",
              details: streamEvent.data.details,
            });
          }

          if (streamEvent.event_type === "fix_proposed") {
            store.addFinding({
              id: streamEvent.data.finding_id || streamEvent.event_id,
              agent_id: streamEvent.agent_id as AgentType,
              severity: streamEvent.data.severity || "info",
              category: streamEvent.data.category || "unknown",
              description: streamEvent.data.description || "",
              proposedFix: streamEvent.data.proposed_fix,
            });
          }

          if (streamEvent.event_type === "fix_verified") {
            store.updateFinding(streamEvent.data.finding_id, {
              fixVerified: streamEvent.data.verification_passed,
            });
          }

          if (streamEvent.event_type === "plan_created") {
            store.setPlan(
              (streamEvent.data.steps || []).map((step: any, idx: number) => ({
                id: idx + 1,
                description: step.description || step,
                status: "pending" as const,
              })),
            );
          }

          if (streamEvent.event_type === "agent_delegated") {
            const stepDesc = streamEvent.data.agent_name || "Task";
            const step = store.plan.find((s) =>
              s.description.toLowerCase().includes(stepDesc.toLowerCase()),
            );
            if (step) {
              store.updatePlanStep(step.id, "in_progress");
            }
          }
        } catch (err) {
          console.error("Failed to parse message:", err);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error("WebSocket error:", error);
        store.setConnected(false);
      };

      wsRef.current.onclose = () => {
        console.log("WebSocket disconnected");
        store.setConnected(false);

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(
            1000 * Math.pow(2, reconnectAttemptsRef.current),
            10000,
          );
          setTimeout(connectWebSocket, delay);
        }
      };
    } catch (err) {
      console.error("Failed to create WebSocket:", err);
      store.setConnected(false);
    }
  }, [reviewId, store]);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connectWebSocket]);

  return {
    isConnected: store.isConnected,
    send: (data: any) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(data));
      }
    },
  };
}
