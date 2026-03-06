"use client";

import { useState, useEffect, useCallback } from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { JsonViewer } from "@/components/ui/JsonViewer";
import {
  searchMemory,
  listThreads,
  listProjects,
  listPendingApprovals,
  listAuditEvents,
  listCommitments,
  getResumeBundle,
} from "@/lib/api";

export default function Dashboard() {
  const [memoryCt, setMemoryCt] = useState<number | null>(null);
  const [threadCt, setThreadCt] = useState<number | null>(null);
  const [projectCt, setProjectCt] = useState<number | null>(null);
  const [approvalCt, setApprovalCt] = useState<number | null>(null);
  const [recentAudit, setRecentAudit] = useState<Record<string, unknown>[]>([]);
  const [overdueCommitments, setOverdueCommitments] = useState<Record<string, unknown>[]>([]);
  const [resumeBundle, setResumeBundle] = useState<Record<string, unknown> | null>(null);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [memRes, thrRes, projRes, appRes, auditRes, commitRes] = await Promise.allSettled([
          searchMemory({ limit: 1 }),
          listThreads({ limit: 1 }),
          listProjects({ limit: 1 }),
          listPendingApprovals(),
          listAuditEvents({ limit: 10 }),
          listCommitments({ overdue: true, limit: 10 }),
        ]);

        if (memRes.status === "fulfilled") setMemoryCt(memRes.value.total);
        if (thrRes.status === "fulfilled") setThreadCt(thrRes.value.total);
        if (projRes.status === "fulfilled") setProjectCt(projRes.value.total);
        if (appRes.status === "fulfilled") {
          const arr = appRes.value as unknown[];
          setApprovalCt(arr.length);
        }
        if (auditRes.status === "fulfilled") {
          setRecentAudit((auditRes.value.items || []) as Record<string, unknown>[]);
        }
        if (commitRes.status === "fulfilled") {
          setOverdueCommitments((commitRes.value.items || []) as Record<string, unknown>[]);
        }
      } catch (e) {
        setError(String(e));
      }
    }
    load();
  }, []);

  const fetchResume = useCallback(async () => {
    setResumeLoading(true);
    try {
      const bundle = await getResumeBundle({ token_budget: 4000 });
      setResumeBundle(bundle);
    } catch (e) {
      setError(String(e));
    } finally {
      setResumeLoading(false);
    }
  }, []);

  const cards = [
    { label: "Memories", count: memoryCt, href: "/memory" },
    { label: "Active Threads", count: threadCt, href: "/threads" },
    { label: "Projects", count: projectCt, href: "/projects" },
    { label: "Pending Approvals", count: approvalCt, href: "/approvals" },
  ];

  return (
    <div className="max-w-6xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button
          onClick={fetchResume}
          disabled={resumeLoading}
          className="px-4 py-2 rounded text-sm font-medium"
          style={{
            backgroundColor: "var(--accent)",
            color: "#fff",
            opacity: resumeLoading ? 0.6 : 1,
          }}
        >
          {resumeLoading ? "Loading..." : "Resume Bundle"}
        </button>
      </div>

      {error && (
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
          {error}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => (
          <a
            key={card.label}
            href={card.href}
            className="rounded-lg p-5 border block hover:opacity-90 transition-opacity"
            style={{
              backgroundColor: "var(--bg-surface)",
              borderColor: "var(--border)",
            }}
          >
            <p className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>
              {card.label}
            </p>
            <p className="text-3xl font-bold mt-1">
              {card.count !== null ? card.count : "—"}
            </p>
          </a>
        ))}
      </div>

      {/* Resume Bundle Panel */}
      {resumeBundle ? (
        <Card title="Resume Bundle">
          <JsonViewer data={resumeBundle} />
        </Card>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Audit Activity */}
        <Card title="Recent Activity">
          {recentAudit.length === 0 ? (
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>No recent activity</p>
          ) : (
            <div className="space-y-2">
              {recentAudit.map((evt, i) => (
                <div
                  key={(evt.id as string) || i}
                  className="flex items-center justify-between py-2 text-sm"
                  style={{ borderBottom: "1px solid var(--border)" }}
                >
                  <div className="flex items-center gap-2">
                    <Badge value={String(evt.event_type || "")} />
                    <span style={{ color: "var(--text-secondary)" }}>
                      {String(evt.entity_type || "")}
                    </span>
                  </div>
                  <span className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>
                    {evt.created_at
                      ? new Date(String(evt.created_at)).toLocaleString()
                      : ""}
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Overdue Commitments */}
        <Card title="Overdue Commitments">
          {overdueCommitments.length === 0 ? (
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>No overdue commitments</p>
          ) : (
            <div className="space-y-2">
              {overdueCommitments.map((c, i) => (
                <div
                  key={(c.id as string) || i}
                  className="py-2 text-sm"
                  style={{ borderBottom: "1px solid var(--border)" }}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{String(c.title || c.description || "Commitment")}</span>
                    <Badge value="overdue" />
                  </div>
                  {c.due_date ? (
                    <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
                      Due: {new Date(String(c.due_date)).toLocaleDateString()}
                    </span>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
