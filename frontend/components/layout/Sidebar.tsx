"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "◆" },
  { href: "/memory", label: "Memory", icon: "◉" },
  { href: "/threads", label: "Threads", icon: "≡" },
  { href: "/projects", label: "Projects", icon: "◫" },
  { href: "/journal", label: "Journal", icon: "✎" },
  { href: "/self-model", label: "Self-Model", icon: "◎" },
  { href: "/approvals", label: "Approvals", icon: "✓" },
  { href: "/audit", label: "Audit Log", icon: "▤" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="w-56 flex-shrink-0 border-r flex flex-col"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border)",
      }}
    >
      {/* Brand */}
      <div className="p-4 border-b" style={{ borderColor: "var(--border)" }}>
        <h2 className="text-lg font-bold tracking-tight">
          <span style={{ color: "var(--accent)" }}>●</span> Becoming
        </h2>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-4 py-2.5 text-sm transition-colors"
              style={{
                backgroundColor: isActive ? "var(--bg-hover)" : "transparent",
                color: isActive
                  ? "var(--text-primary)"
                  : "var(--text-secondary)",
                borderRight: isActive
                  ? "2px solid var(--accent)"
                  : "2px solid transparent",
              }}
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div
        className="p-4 border-t text-xs"
        style={{
          borderColor: "var(--border)",
          color: "var(--text-secondary)",
        }}
      >
        v0.1.0 · MVP
      </div>
    </aside>
  );
}
