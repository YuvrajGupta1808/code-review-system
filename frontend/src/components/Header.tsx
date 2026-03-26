/**
 * Top navigation header with controls
 */

import { useStore } from "../store";
import { Moon, Sun, Wifi, WifiOff } from "lucide-react";
import clsx from "clsx";
import { motion } from "framer-motion";

export function Header() {
  const { theme, toggleTheme, isConnected } = useStore();

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Logo/Title */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <span className="text-white font-bold text-lg">◆</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Code Review
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Multi-Agent Analysis
            </p>
          </div>
        </div>

        {/* Center - Status */}
        <div className="flex items-center gap-2">
          <motion.div
            animate={{
              scale: isConnected ? [1, 1.1, 1] : 1,
            }}
            transition={{ duration: 1, repeat: Infinity }}
            className="flex items-center gap-2"
          >
            {isConnected ? (
              <>
                <motion.div
                  animate={{ opacity: [0.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                  className="w-2 h-2 rounded-full bg-green-500"
                />
                <span className="text-sm font-medium text-green-600 dark:text-green-400">
                  Connected
                </span>
                <Wifi className="w-4 h-4 text-green-600 dark:text-green-400" />
              </>
            ) : (
              <>
                <div className="w-2 h-2 rounded-full bg-gray-400" />
                <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Disconnected
                </span>
                <WifiOff className="w-4 h-4 text-gray-600 dark:text-gray-400" />
              </>
            )}
          </motion.div>
        </div>

        {/* Right - Theme toggle */}
        <button
          onClick={toggleTheme}
          className={clsx(
            "p-2 rounded-lg transition-colors",
            "bg-gray-100 dark:bg-gray-800",
            "text-gray-600 dark:text-gray-400",
            "hover:bg-gray-200 dark:hover:bg-gray-700",
          )}
          title="Toggle theme"
        >
          {theme === "light" ? (
            <Moon className="w-5 h-5" />
          ) : (
            <Sun className="w-5 h-5" />
          )}
        </button>
      </div>
    </header>
  );
}
