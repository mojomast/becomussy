"use client";

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  // Status
  active: { bg: "#16a34a20", text: "#22c55e" },
  completed: { bg: "#16a34a20", text: "#22c55e" },
  archived: { bg: "#6b728020", text: "#9ca3af" },
  deprecated: { bg: "#eab30820", text: "#eab308" },
  paused: { bg: "#eab30820", text: "#eab308" },
  blocked: { bg: "#ef444420", text: "#ef4444" },
  cancelled: { bg: "#6b728020", text: "#9ca3af" },

  // Risk
  low: { bg: "#16a34a20", text: "#22c55e" },
  medium: { bg: "#eab30820", text: "#eab308" },
  high: { bg: "#ef444420", text: "#ef4444" },

  // Approval
  approved: { bg: "#16a34a20", text: "#22c55e" },
  pending: { bg: "#eab30820", text: "#eab308" },
  pending_review: { bg: "#eab30820", text: "#eab308" },
  approval_required: { bg: "#eab30820", text: "#eab308" },
  rejected: { bg: "#ef444420", text: "#ef4444" },
  deferred: { bg: "#3b82f620", text: "#3b82f6" },

  // Memory types
  episodic: { bg: "#6366f120", text: "#818cf8" },
  semantic: { bg: "#8b5cf620", text: "#a78bfa" },
  procedural: { bg: "#06b6d420", text: "#22d3ee" },
  working: { bg: "#f9731620", text: "#fb923c" },

  // Journal types
  reflection: { bg: "#6366f120", text: "#818cf8" },
  observation: { bg: "#06b6d420", text: "#22d3ee" },
  decision: { bg: "#eab30820", text: "#eab308" },
  synthesis: { bg: "#8b5cf620", text: "#a78bfa" },
  session_end: { bg: "#f9731620", text: "#fb923c" },

  // Diff categories
  added_theme: { bg: "#16a34a20", text: "#22c55e" },
  removed_theme: { bg: "#ef444420", text: "#ef4444" },
  modified_theme: { bg: "#eab30820", text: "#eab308" },

  // Urgency
  urgent: { bg: "#ef444420", text: "#ef4444" },
  normal: { bg: "#6b728020", text: "#9ca3af" },

  // Default
  default: { bg: "#6b728020", text: "#9ca3af" },
};

interface BadgeProps {
  value: string;
  className?: string;
}

export function Badge({ value, className = "" }: BadgeProps) {
  const normalized = (value || "").toLowerCase().replace(/\s+/g, "_");
  const colors = STATUS_COLORS[normalized] || STATUS_COLORS.default;

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${className}`}
      style={{
        backgroundColor: colors.bg,
        color: colors.text,
      }}
    >
      {value}
    </span>
  );
}
