/**
 * Live stream of agent reasoning and thoughts
 */

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useStore } from "../store";
import clsx from "clsx";

const agentColors: Record<string, string> = {
  coordinator:
    "bg-purple-100 dark:bg-purple-900/30 text-purple-900 dark:text-purple-100",
  security_agent:
    "bg-red-100 dark:bg-red-900/30 text-red-900 dark:text-red-100",
  bug_agent: "bg-blue-100 dark:bg-blue-900/30 text-blue-900 dark:text-blue-100",
};

const agentLabels: Record<string, string> = {
  coordinator: "Coordinator",
  security_agent: "Security Agent",
  bug_agent: "Bug Agent",
};

export function ThoughtStreamPanel() {
  const { thoughts } = useStore();
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest thought
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [thoughts.length]);

  // Group thoughts by agent
  const latestThoughts = thoughts.slice(-5);
  const groupedByAgent = latestThoughts.reduce(
    (acc, thought) => {
      const agent = thought.agent_id;
      if (!acc[agent]) acc[agent] = [];
      acc[agent].push(thought);
      return acc;
    },
    {} as Record<string, typeof thoughts>,
  );

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6 flex flex-col h-full">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        LIVE THOUGHTS
      </h2>

      <div ref={containerRef} className="flex-1 overflow-y-auto space-y-4 pr-2">
        <AnimatePresence mode="popLayout">
          {Object.entries(groupedByAgent).map(([agentId, agentThoughts]) => (
            <div key={agentId} className="space-y-2">
              <div
                className={clsx(
                  "px-3 py-1.5 rounded-full text-xs font-semibold w-fit",
                  agentColors[agentId],
                )}
              >
                {agentLabels[agentId]} - Thinking
              </div>
              {agentThoughts.map((thought, idx) => (
                <motion.div
                  key={thought.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3, delay: idx * 0.05 }}
                  className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed pl-4 border-l-2 border-gray-300 dark:border-gray-700"
                >
                  {thought.content}
                  {idx === agentThoughts.length - 1 && (
                    <motion.span
                      animate={{ opacity: [1, 0.3] }}
                      transition={{ duration: 0.8, repeat: Infinity }}
                      className="inline ml-1"
                    >
                      █
                    </motion.span>
                  )}
                </motion.div>
              ))}
            </div>
          ))}
        </AnimatePresence>

        {thoughts.length === 0 && (
          <div className="text-center text-gray-500 dark:text-gray-400 py-8">
            <p className="text-sm">Waiting for agent analysis...</p>
          </div>
        )}
      </div>
    </div>
  );
}
