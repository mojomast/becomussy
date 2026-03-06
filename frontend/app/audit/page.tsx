"use client";

import { useState, useEffect, useCallback } from "react";
import { Badge } from "@/components/ui/Badge";
import { JsonViewer } from "@/components/ui/JsonViewer";
import { DataTable } from "@/components/ui/DataTable";
import { listAuditEvents } from "@/lib/api";

export default function AuditPage() {
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 25;
  const [eventTypeFilter, setEventTypeFilter] = useState("");
  const [entityTypeFilter, setEntityTypeFilter] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listAuditEvents({
        event_type: eventTypeFilter || undefined,
        entity_type: entityTypeFilter || undefined,
        limit,
        offset,
      });
      setItems((res.items || []) as Record<string, unknown>[]);
      setTotal(res.total || 0);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, [eventTypeFilter, entityTypeFilter, offset]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const inputStyle = {
    backgroundColor: "var(--bg)",
    borderColor: "var(--border)",
    color: "var(--text-primary)",
  };

  const columns = [
    {
      key: "created_at",
      label: "Timestamp",
      render: (row: Record<string, unknown>) => (
        <span className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>
          {row.created_at ? new Date(String(row.created_at)).toLocaleString() : "—"}
        </span>
      ),
    },
    {
      key: "event_type",
      label: "Event",
      render: (row: Record<string, unknown>) => <Badge value={String(row.event_type || "")} />,
    },
    {
      key: "entity_type",
      label: "Entity Type",
      render: (row: Record<string, unknown>) => (
        <span className="text-xs">{String(row.entity_type || "—")}</span>
      ),
    },
    {
      key: "actor",
      label: "Actor",
      render: (row: Record<string, unknown>) => (
        <span className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>
          {String(row.actor || row.actor_id || "—")}
        </span>
      ),
    },
    {
      key: "entity_id",
      label: "Entity ID",
      render: (row: Record<string, unknown>) => (
        <code className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>
          {row.entity_id ? String(row.entity_id).slice(0, 12) + "..." : "—"}
        </code>
      ),
    },
    {
      key: "expand",
      label: "",
      render: (row: Record<string, unknown>) => (
        <span className="text-xs" style={{ color: "var(--accent)" }}>
          {expandedId === row.id ? "▾" : "▸"}
        </span>
      ),
    },
  ];

  return (
    <div className="max-w-6xl space-y-4">
      <h1 className="text-2xl font-bold">Audit Log</h1>

      {error && (
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
          {error}
        </div>
      )}

      <div className="flex gap-3 items-center">
        <select
          value={eventTypeFilter}
          onChange={(e) => { setEventTypeFilter(e.target.value); setOffset(0); }}
          className="px-3 py-2 rounded border text-sm"
          style={inputStyle}
        >
          <option value="">All Event Types</option>
          <option value="created">Created</option>
          <option value="updated">Updated</option>
          <option value="deleted">Deleted</option>
          <option value="reinforced">Reinforced</option>
          <option value="contradicted">Contradicted</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="deferred">Deferred</option>
        </select>
        <select
          value={entityTypeFilter}
          onChange={(e) => { setEntityTypeFilter(e.target.value); setOffset(0); }}
          className="px-3 py-2 rounded border text-sm"
          style={inputStyle}
        >
          <option value="">All Entity Types</option>
          <option value="memory">Memory</option>
          <option value="thread">Thread</option>
          <option value="project">Project</option>
          <option value="commitment">Commitment</option>
          <option value="journal">Journal</option>
          <option value="self_model">Self-Model</option>
          <option value="revision">Revision</option>
        </select>
      </div>

      <div className="rounded-lg border" style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border)" }}>
        <DataTable
          columns={columns}
          rows={items}
          loading={loading}
          emptyMessage="No audit events found"
          total={total}
          limit={limit}
          offset={offset}
          onPageChange={setOffset}
          onRowClick={(row) => {
            setExpandedId(expandedId === row.id ? null : String(row.id));
          }}
        />
      </div>

      {/* Expanded detail - shown below the table for the selected row */}
      {expandedId ? (() => {
        const row = items.find((i) => i.id === expandedId);
        if (!row) return null;
        return (
          <div
            className="rounded-lg border p-4"
            style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border)" }}
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold">Event Detail</h3>
              <button
                onClick={() => setExpandedId(null)}
                className="text-xs"
                style={{ color: "var(--text-secondary)" }}
              >
                Close ×
              </button>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Full Entity ID</p>
                <code className="text-xs font-mono">{String(row.entity_id || "")}</code>
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Event ID</p>
                <code className="text-xs font-mono">{String(row.id || "")}</code>
              </div>
            </div>
            {row.before_state ? (
              <div className="mb-3">
                <JsonViewer data={row.before_state} label="Before State" collapsed />
              </div>
            ) : null}
            {row.after_state ? (
              <div className="mb-3">
                <JsonViewer data={row.after_state} label="After State" collapsed />
              </div>
            ) : null}
            {row.metadata ? (
              <div className="mb-3">
                <JsonViewer data={row.metadata} label="Metadata" collapsed />
              </div>
            ) : null}
            {/* Full event JSON */}
            <JsonViewer data={row} label="Full Event JSON" collapsed />
          </div>
        );
      })() : null}
    </div>
  );
}
