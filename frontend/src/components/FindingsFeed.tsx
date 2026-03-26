/**
 * Feed of discovered issues/findings
 */

import { motion, AnimatePresence } from "framer-motion";
import { useStore } from "../store";
import {
  ChevronDown,
  AlertCircle,
  AlertTriangle,
  AlertOctagon,
  Info,
} from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

const severityConfig: Record<string, { icon: any; color: string; bg: string }> =
  {
    critical: {
      icon: AlertOctagon,
      color: "text-white",
      bg: "bg-red-600 dark:bg-red-700",
    },
    high: {
      icon: AlertTriangle,
      color: "text-white",
      bg: "bg-orange-600 dark:bg-orange-700",
    },
    medium: {
      icon: AlertCircle,
      color: "text-white",
      bg: "bg-yellow-600 dark:bg-yellow-700",
    },
    low: {
      icon: Info,
      color: "text-white",
      bg: "bg-blue-600 dark:bg-blue-700",
    },
    info: {
      icon: Info,
      color: "text-white",
      bg: "bg-gray-600 dark:bg-gray-700",
    },
  };

const categoryLabels: Record<string, string> = {
  sql_injection: "🔴 SQL Injection",
  xss: "🔴 XSS Vulnerability",
  hardcoded_secret: "🔴 Hardcoded Secret",
  null_reference: "🟡 Null Reference",
  logic_error: "🟡 Logic Error",
  race_condition: "🟡 Race Condition",
  type_mismatch: "🔵 Type Mismatch",
  resource_leak: "🟡 Resource Leak",
  auth_bypass: "🔴 Auth Bypass",
  error_handling: "🟡 Error Handling",
};

interface FindingItemProps {
  id: string;
}

function FindingItem({ id }: FindingItemProps) {
  const { findings, selectedFindingId, setSelectedFindingId } = useStore();
  const finding = findings.find((f) => f.id === id);
  const [expanded, setExpanded] = useState(false);
  const isSelected = selectedFindingId === id;

  if (!finding) return null;

  const config = severityConfig[finding.severity];
  const IconComponent = config.icon;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className={clsx(
        "border rounded-lg overflow-hidden transition-all",
        isSelected
          ? "border-gray-400 dark:border-gray-600 bg-gray-50 dark:bg-gray-800"
          : "border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900",
      )}
    >
      <button
        onClick={() => {
          setSelectedFindingId(isSelected ? undefined : id);
          setExpanded(!expanded);
        }}
        className="w-full p-4 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-start gap-4"
      >
        <div className={clsx("p-2 rounded-lg flex-shrink-0", config.bg)}>
          <IconComponent className={clsx("w-5 h-5", config.color)} />
        </div>

        <div className="flex-1 text-left">
          <div className="flex items-start justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  {categoryLabels[finding.category] || finding.category}
                </h3>
                {finding.line && (
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    line {finding.line}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {finding.description}
              </p>
            </div>
            <ChevronDown
              className={clsx(
                "w-5 h-5 text-gray-400 flex-shrink-0 transition-transform",
                expanded && "rotate-180",
              )}
            />
          </div>
        </div>
      </button>

      <AnimatePresence>
        {(expanded || isSelected) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-gray-200 dark:border-gray-800 p-4 space-y-3 bg-gray-50 dark:bg-gray-800/50"
          >
            {finding.details && (
              <div>
                <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Details
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  {finding.details}
                </p>
              </div>
            )}

            {finding.proposedFix && (
              <div>
                <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Proposed Fix
                </p>
                <pre className="bg-gray-100 dark:bg-gray-900 p-3 rounded text-xs text-gray-700 dark:text-gray-300 overflow-x-auto">
                  {finding.proposedFix}
                </pre>
              </div>
            )}

            {finding.fixVerified !== undefined && (
              <div className="flex items-center gap-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <div
                  className={clsx(
                    "w-2 h-2 rounded-full",
                    finding.fixVerified ? "bg-green-500" : "bg-red-500",
                  )}
                />
                <span className="text-xs font-medium">
                  {finding.fixVerified
                    ? "Fix Verified"
                    : "Fix Verification Failed"}
                </span>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function FindingsFeed() {
  const { findings } = useStore();

  // Sort by severity (critical first)
  const sortedFindings = [...findings].sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
    return (severityOrder[a.severity] ?? 4) - (severityOrder[b.severity] ?? 4);
  });

  // Summary stats
  const stats = {
    critical: findings.filter((f) => f.severity === "critical").length,
    high: findings.filter((f) => f.severity === "high").length,
    medium: findings.filter((f) => f.severity === "medium").length,
    low: findings.filter((f) => f.severity === "low").length,
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6 flex flex-col h-full">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          FINDINGS
        </h2>

        {/* Summary stats */}
        <div className="grid grid-cols-4 gap-2">
          {[
            {
              label: "Critical",
              value: stats.critical,
              color:
                "bg-red-100 dark:bg-red-900/30 text-red-900 dark:text-red-100",
            },
            {
              label: "High",
              value: stats.high,
              color:
                "bg-orange-100 dark:bg-orange-900/30 text-orange-900 dark:text-orange-100",
            },
            {
              label: "Medium",
              value: stats.medium,
              color:
                "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-900 dark:text-yellow-100",
            },
            {
              label: "Low",
              value: stats.low,
              color:
                "bg-blue-100 dark:bg-blue-900/30 text-blue-900 dark:text-blue-100",
            },
          ].map((stat) => (
            <div
              key={stat.label}
              className={clsx("p-2 rounded text-center", stat.color)}
            >
              <div className="text-lg font-bold">{stat.value}</div>
              <div className="text-xs font-medium">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 pr-2">
        <AnimatePresence mode="popLayout">
          {sortedFindings.map((finding) => (
            <FindingItem key={finding.id} id={finding.id} />
          ))}
        </AnimatePresence>

        {findings.length === 0 && (
          <div className="text-center text-gray-500 dark:text-gray-400 py-8">
            <p className="text-sm">No findings yet...</p>
          </div>
        )}
      </div>
    </div>
  );
}
