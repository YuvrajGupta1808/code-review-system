/**
 * Shows the execution plan and progress
 */

import { motion } from "framer-motion";
import { useStore } from "../store";
import { CheckCircle2, Circle, Loader } from "lucide-react";
import clsx from "clsx";

export function ExecutionPlanPanel() {
  const { plan } = useStore();

  if (plan.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          EXECUTION PLAN
        </h2>
        <div className="text-center text-gray-500 dark:text-gray-400 py-8">
          <p className="text-sm">Plan will appear once analysis starts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        EXECUTION PLAN
      </h2>

      <div className="space-y-3">
        {plan.map((step, idx) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="flex items-center gap-3"
          >
            {/* Step indicator */}
            <div className="flex-shrink-0 w-6 h-6 flex items-center justify-center">
              {step.status === "completed" && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring" }}
                >
                  <CheckCircle2 className="w-6 h-6 text-green-500" />
                </motion.div>
              )}
              {step.status === "in_progress" && (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                >
                  <Loader className="w-6 h-6 text-blue-500" />
                </motion.div>
              )}
              {step.status === "pending" && (
                <Circle className="w-6 h-6 text-gray-300 dark:text-gray-700" />
              )}
            </div>

            {/* Step content */}
            <div className="flex-1 min-w-0">
              <p
                className={clsx("text-sm font-medium", {
                  "text-gray-900 dark:text-white":
                    step.status === "in_progress",
                  "text-gray-700 dark:text-gray-300":
                    step.status === "completed",
                  "text-gray-400 dark:text-gray-600": step.status === "pending",
                })}
              >
                {step.id}. {step.description}
              </p>
            </div>

            {/* Status badge */}
            <motion.div
              animate={{
                opacity: step.status === "in_progress" ? [0.7, 1] : 1,
              }}
              transition={{ duration: 0.6, repeat: Infinity }}
              className={clsx(
                "text-xs font-semibold px-2 py-1 rounded whitespace-nowrap",
                {
                  "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400":
                    step.status === "completed",
                  "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400":
                    step.status === "in_progress",
                  "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400":
                    step.status === "pending",
                },
              )}
            >
              {step.status === "completed" && "✓"}
              {step.status === "in_progress" && "→"}
              {step.status === "pending" && "○"}
            </motion.div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
