"use client";

import { useState } from "react";

interface JsonViewerProps {
  data: unknown;
  collapsed?: boolean;
  label?: string;
}

export function JsonViewer({ data, collapsed = false, label }: JsonViewerProps) {
  const [isCollapsed, setIsCollapsed] = useState(collapsed);

  if (data === null || data === undefined) {
    return (
      <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
        null
      </span>
    );
  }

  const jsonString = typeof data === "string" ? data : JSON.stringify(data, null, 2);

  return (
    <div>
      {label && (
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="flex items-center gap-1 text-xs font-medium mb-1 hover:opacity-80"
          style={{ color: "var(--text-secondary)" }}
        >
          <span>{isCollapsed ? "▸" : "▾"}</span>
          {label}
        </button>
      )}
      {!isCollapsed && (
        <pre
          className="text-xs font-mono p-3 rounded overflow-x-auto whitespace-pre-wrap break-all"
          style={{
            backgroundColor: "var(--bg)",
            color: "var(--text-primary)",
            border: "1px solid var(--border)",
          }}
        >
          {jsonString}
        </pre>
      )}
    </div>
  );
}
