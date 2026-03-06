"use client";

interface EmptyStateProps {
  message?: string;
  icon?: string;
  action?: React.ReactNode;
}

export function EmptyState({
  message = "Nothing here yet",
  icon = "∅",
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <span className="text-4xl mb-3 opacity-30">{icon}</span>
      <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>
        {message}
      </p>
      {action && <div>{action}</div>}
    </div>
  );
}
