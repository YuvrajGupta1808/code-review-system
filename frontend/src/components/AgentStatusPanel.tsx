/**
 * Panel showing real-time status of all agents
 */

import { motion } from "framer-motion";
import { useStore } from "../store";
import clsx from "clsx";

const statusColors: Record<string, string> = {
  idle: "bg-gray-300 dark:bg-gray-600",
  thinking: "bg-blue-500 animate-pulse",
  tool_calling: "bg-amber-500 animate-pulse",
  completed: "bg-green-500",
  error: "bg-red-500",
};

const statusLabels: Record<string, string> = {
  idle: "IDLE",
  thinking: "THINKING",
  tool_calling: "TOOL CALLING",
  completed: "COMPLETED",
  error: "ERROR",
};

export function AgentStatusPanel() {
  const { agents } = useStore();
  const agentList = Array.from(agents.values());

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        AGENTS
      </h2>

      <div className="space-y-3">
        {agentList.map((agent) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <div className="flex items-center gap-3 flex-1">
              <motion.div
                animate={{
                  scale:
                    agent.status === "thinking" ||
                    agent.status === "tool_calling"
                      ? [1, 1.2, 1]
                      : 1,
                }}
                transition={{ duration: 1, repeat: Infinity }}
                className={clsx(
                  "w-3 h-3 rounded-full",
                  statusColors[agent.status],
                )}
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {agent.name}
              </span>
            </div>

            <motion.div
              animate={{
                opacity:
                  agent.status === "thinking" || agent.status === "tool_calling"
                    ? [0.6, 1]
                    : 1,
              }}
              transition={{ duration: 0.6, repeat: Infinity }}
              className={clsx(
                "px-3 py-1 rounded text-xs font-semibold text-white",
                {
                  "bg-gray-400": agent.status === "idle",
                  "bg-blue-500": agent.status === "thinking",
                  "bg-amber-500": agent.status === "tool_calling",
                  "bg-green-500": agent.status === "completed",
                  "bg-red-500": agent.status === "error",
                },
              )}
            >
              {statusLabels[agent.status]}
            </motion.div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
