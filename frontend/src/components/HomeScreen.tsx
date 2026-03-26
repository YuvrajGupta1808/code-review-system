/**
 * Home Screen - Initial screen with file upload and text editor options
 * Minimal, professional IDE-inspired design with pure black background
 */

import { useStore } from "../store";
import { Upload, FileText, Zap } from "lucide-react";
import { motion } from "framer-motion";
import { useRef } from "react";

export function HomeScreen() {
  const { setUiMode, setCodeContent, setFileName } = useStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file size (limit to 1MB for reasonable code files)
    if (file.size > 1024 * 1024) {
      alert("File size exceeds 1MB. Please choose a smaller file.");
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setFileName(file.name);
      setCodeContent(content);
      setUiMode("editor");
    };
    reader.readAsText(file);
  };

  const handleStartWriting = () => {
    setFileName("untitled.js");
    setCodeContent("");
    setUiMode("editor");
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 12 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4, ease: "easeOut" },
    },
  };

  return (
    <div className="min-h-screen bg-code-bg text-code-text flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="px-6 py-8 border-b border-code-border"
      >
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded flex items-center justify-center bg-code-accent">
              <Zap size={18} className="text-code-bg" strokeWidth={2.5} />
            </div>
            <h1 className="text-2xl font-semibold tracking-tight">
              CodeReview
            </h1>
          </div>
          <p className="text-code-text-muted text-sm">
            Professional code analysis powered by multi-agent AI
          </p>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <motion.div
          className="w-full max-w-3xl"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Title Section */}
          <motion.div variants={itemVariants} className="text-center mb-12">
            <h2 className="text-5xl font-bold mb-3 tracking-tight">
              Get Started
            </h2>
            <p className="text-code-text-muted">
              Choose how you'd like to analyze your code
            </p>
          </motion.div>

          {/* Options Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
            {/* Upload File Option */}
            <motion.button
              variants={itemVariants}
              onClick={() => fileInputRef.current?.click()}
              className="group relative rounded-lg border border-code-border hover:border-code-accent
                         bg-code-bg-subtle hover:bg-code-surface transition-all p-7
                         flex flex-col items-start justify-start text-left h-48
                         focus:outline-none focus:ring-2 focus:ring-code-accent focus:ring-offset-2 focus:ring-offset-code-bg"
            >
              {/* Subtle hover background */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-10 bg-code-accent rounded-lg transition-opacity" />

              <div className="relative z-10 w-full h-full flex flex-col">
                {/* Icon Container */}
                <div
                  className="w-10 h-10 rounded flex items-center justify-center
                               bg-code-surface group-hover:bg-code-border transition-colors mb-4"
                >
                  <Upload
                    size={20}
                    className="text-code-accent group-hover:text-code-accent-hover transition-colors"
                    strokeWidth={1.5}
                  />
                </div>

                {/* Content */}
                <div className="flex-1">
                  <h3 className="text-sm font-semibold mb-1 group-hover:text-code-accent-hover transition-colors">
                    Upload File
                  </h3>
                  <p className="text-xs text-code-text-muted group-hover:text-code-text-secondary transition-colors">
                    Upload a code file from your computer
                  </p>
                </div>

                {/* Supported formats - bottom */}
                <p className="text-xs text-code-text-muted group-hover:text-code-text-secondary transition-colors">
                  JS, TS, Python, Java, Go, Rust, etc.
                </p>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileUpload}
                className="hidden"
                accept=".js,.ts,.jsx,.tsx,.py,.java,.cpp,.c,.go,.rs,.rb,.php,.swift,.kt,.scala,.r,.sql,.json,.yaml,.xml,.html,.css"
                aria-label="Upload code file"
              />
            </motion.button>

            {/* Write Code Option */}
            <motion.button
              variants={itemVariants}
              onClick={handleStartWriting}
              className="group relative rounded-lg border border-code-border hover:border-code-accent
                         bg-code-bg-subtle hover:bg-code-surface transition-all p-7
                         flex flex-col items-start justify-start text-left h-48
                         focus:outline-none focus:ring-2 focus:ring-code-accent focus:ring-offset-2 focus:ring-offset-code-bg"
            >
              {/* Subtle hover background */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-10 bg-code-accent rounded-lg transition-opacity" />

              <div className="relative z-10 w-full h-full flex flex-col">
                {/* Icon Container */}
                <div
                  className="w-10 h-10 rounded flex items-center justify-center
                               bg-code-surface group-hover:bg-code-border transition-colors mb-4"
                >
                  <FileText
                    size={20}
                    className="text-code-accent group-hover:text-code-accent-hover transition-colors"
                    strokeWidth={1.5}
                  />
                </div>

                {/* Content */}
                <div className="flex-1">
                  <h3 className="text-sm font-semibold mb-1 group-hover:text-code-accent-hover transition-colors">
                    Write Code
                  </h3>
                  <p className="text-xs text-code-text-muted group-hover:text-code-text-secondary transition-colors">
                    Paste or write code directly in the editor
                  </p>
                </div>

                {/* Action indicator */}
                <p className="text-xs text-code-text-muted group-hover:text-code-text-secondary transition-colors">
                  Start with an empty editor
                </p>
              </div>
            </motion.button>
          </div>

          {/* Info Card */}
          <motion.div
            variants={itemVariants}
            className="bg-code-bg-subtle border border-code-border rounded-lg p-5 text-sm"
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                <Zap size={16} className="text-code-accent" strokeWidth={2} />
              </div>
              <div>
                <h3 className="font-semibold text-code-text mb-1">
                  Multi-Agent Analysis
                </h3>
                <p className="text-code-text-muted text-xs">
                  Your code will be analyzed by specialized agents for security
                  vulnerabilities, bugs, and code quality issues in real-time.
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.4 }}
        className="border-t border-code-border px-6 py-4 text-center text-xs text-code-text-muted"
      >
        <p>Professional code analysis powered by multi-agent AI</p>
      </motion.div>
    </div>
  );
}
