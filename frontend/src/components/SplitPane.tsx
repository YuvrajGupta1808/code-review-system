/**
 * Resizable Split Pane Component
 * Allows dragging to resize panels with smooth interactions
 * Minimal dark theme with subtle hover states
 */

import { useState, useRef, ReactNode } from "react";
import clsx from "clsx";

interface SplitPaneProps {
  orientation: "horizontal" | "vertical";
  defaultSize?: number;
  minSize?: number;
  maxSize?: number;
  children: [ReactNode, ReactNode];
}

export function SplitPane({
  orientation,
  defaultSize = 50,
  minSize = 20,
  maxSize = 80,
  children,
}: SplitPaneProps) {
  const [size, setSize] = useState(defaultSize);
  const containerRef = useRef<HTMLDivElement>(null);
  const isResizing = useRef(false);

  const handleMouseDown = () => {
    isResizing.current = true;
    document.body.style.userSelect = "none";
    document.body.style.cursor =
      orientation === "vertical" ? "row-resize" : "col-resize";
  };

  const handleMouseUp = () => {
    isResizing.current = false;
    document.body.style.userSelect = "auto";
    document.body.style.cursor = "default";
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isResizing.current || !containerRef.current) return;

    const container = containerRef.current;
    const rect = container.getBoundingClientRect();

    let newSize: number;

    if (orientation === "horizontal") {
      const percentage = ((e.clientX - rect.left) / rect.width) * 100;
      newSize = Math.max(minSize, Math.min(maxSize, percentage));
    } else {
      const percentage = ((e.clientY - rect.top) / rect.height) * 100;
      newSize = Math.max(minSize, Math.min(maxSize, percentage));
    }

    setSize(newSize);
  };

  const isVertical = orientation === "vertical";

  return (
    <div
      ref={containerRef}
      className={clsx("flex h-full bg-code-bg", {
        "flex-row": !isVertical,
        "flex-col": isVertical,
      })}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* First Pane */}
      <div
        style={{
          [isVertical ? "height" : "width"]: `${size}%`,
          flex: "none",
        }}
        className="overflow-hidden"
      >
        {children[0]}
      </div>

      {/* Divider - Minimal design with subtle hover effect */}
      <div
        onMouseDown={handleMouseDown}
        className={clsx(
          "group transition-all duration-150 active:bg-code-accent",
          {
            "w-px hover:w-1 hover:bg-code-accent hover:bg-opacity-30 bg-code-border cursor-col-resize":
              !isVertical,
            "h-px hover:h-1 hover:bg-code-accent hover:bg-opacity-30 bg-code-border cursor-row-resize":
              isVertical,
          },
        )}
        style={{
          backgroundColor: isResizing.current ? "#4a9eff" : undefined,
          transition:
            "background-color 0.1s ease, width 0.15s ease, height 0.15s ease",
        }}
      />

      {/* Second Pane */}
      <div
        style={{
          [isVertical ? "height" : "width"]: `${100 - size}%`,
          flex: "none",
        }}
        className="overflow-hidden"
      >
        {children[1]}
      </div>
    </div>
  );
}
