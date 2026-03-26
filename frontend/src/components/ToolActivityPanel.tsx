/**
 * Log of all tool invocations with inputs and outputs
 */

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useStore } from "../store";
import { formatTime } from "../utils/format";

const agentColors: Record<string, string> = {
  coordinator: "text-purple-600 dark:text-purple-400",
  security_agent: "text-red-600 dark:text-red-400",
  bug_agent: "text-blue-600 dark:text-blue-400",
};

const agentLabels: Record<string, string> = {
  coordinator: "Coordinator",
  security_agent: "SecurityAgent",
  bug_agent: "BugAgent",
};

export function ToolActivityPanel() {
  const { toolCalls } = useStore();
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest tool call
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [toolCalls.length]);

  const recentToolCalls = toolCalls.slice(-8);

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6 flex flex-col h-full">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        TOOL CALLS
      </h2>

      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto space-y-4 font-mono text-xs pr-2"
      >
        <AnimatePresence mode="popLayout">
          {recentToolCalls.map((toolCall) => (
            <motion.div
              key={toolCall.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded p-3 space-y-2"
            >
              {/* Header with time and agent */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 dark:text-gray-400">
                    {formatTime(toolCall.timestamp)}
                  </span>
                  <span
                    className={clsx(
                      "font-semibold",
                      agentColors[toolCall.agent_id],
                    )}
                  >
                    [{agentLabels[toolCall.agent_id]}]
                  </span>
                  <span className="text-blue-600 dark:text-blue-400 font-semibold">
                    {toolCall.tool_name}
                  </span>
                </div>
                {toolCall.duration_ms && (
                  <span className="text-gray-500 dark:text-gray-400 ml-auto">
                    {toolCall.duration_ms}ms
                  </span>
                )}
              </div>

              {/* Input */}
              {Object.keys(toolCall.input).length > 0 && (
                <div>
                  <span className="text-gray-600 dark:text-gray-400">
                    Input:
                  </span>
                  <pre className="bg-gray-100 dark:bg-gray-900 p-2 rounded mt-1 overflow-x-auto text-xs text-gray-700 dark:text-gray-300">
                    {JSON.stringify(toolCall.input, null, 2)}
                  </pre>
                </div>
              )}

              {/* Output */}
              {toolCall.output && Object.keys(toolCall.output).length > 0 && (
                <div>
                  <span className="text-green-600 dark:text-green-400">
                    Output:
                  </span>
                  <pre className="bg-gray-100 dark:bg-gray-900 p-2 rounded mt-1 overflow-x-auto text-xs text-gray-700 dark:text-gray-300">
                    {JSON.stringify(toolCall.output, null, 2)}
                  </pre>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {toolCalls.length === 0 && (
          <div className="text-center text-gray-500 dark:text-gray-400 py-8">
            <p className="text-sm">No tool calls yet...</p>
          </div>
        )}
      </div>
    </div>
  );
}

function clsx(...classes: any[]) {
  return classes.filter(Boolean).join(" ");
}
