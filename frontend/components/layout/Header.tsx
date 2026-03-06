"use client";

export function Header() {
  return (
    <header
      className="h-14 flex items-center justify-between px-6 border-b flex-shrink-0"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border)",
      }}
    >
      <h1 className="text-base font-semibold">becomussy</h1>

      <div className="flex items-center gap-4">
        <span
          className="text-xs px-2 py-1 rounded"
          style={{
            backgroundColor: "var(--bg-hover)",
            color: "var(--text-secondary)",
          }}
        >
          development
        </span>
        <span
          className="text-sm"
          style={{ color: "var(--text-secondary)" }}
        >
          admin
        </span>
      </div>
    </header>
  );
}
