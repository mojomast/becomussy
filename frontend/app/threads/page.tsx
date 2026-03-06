"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { DataTable } from "@/components/ui/DataTable";
import { listThreads, createThread } from "@/lib/api";

export default function ThreadsPage() {
  const router = useRouter();
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 20;
  const [statusFilter, setStatusFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: "",
    description: "",
    urgency: "normal",
    importance: "0.5",
    next_action: "",
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listThreads({
        status: statusFilter || undefined,
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
  }, [statusFilter, offset]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createThread({
        title: createForm.title,
        description: createForm.description || undefined,
        urgency: createForm.urgency,
        importance: parseFloat(createForm.importance),
        next_action: createForm.next_action || undefined,
      });
      setShowCreate(false);
      setCreateForm({ title: "", description: "", urgency: "normal", importance: "0.5", next_action: "" });
      fetchData();
    } catch (e) {
      setError(String(e));
    }
  };

  const inputStyle = {
    backgroundColor: "var(--bg)",
    borderColor: "var(--border)",
    color: "var(--text-primary)",
  };

  const columns = [
    {
      key: "title",
      label: "Title",
      className: "max-w-xs",
      render: (row: Record<string, unknown>) => (
        <span className="font-medium">{String(row.title || "Untitled")}</span>
      ),
    },
    {
      key: "status",
      label: "Status",
      render: (row: Record<string, unknown>) => <Badge value={String(row.status || "")} />,
    },
    {
      key: "urgency",
      label: "Urgency",
      render: (row: Record<string, unknown>) => <Badge value={String(row.urgency || "normal")} />,
    },
    {
      key: "importance",
      label: "Importance",
      render: (row: Record<string, unknown>) => (
        <span className="font-mono text-xs">{row.importance != null ? Number(row.importance).toFixed(2) : "—"}</span>
      ),
    },
    {
      key: "next_action",
      label: "Next Action",
      className: "max-w-xs truncate",
      render: (row: Record<string, unknown>) => (
        <span className="truncate block max-w-xs text-xs" style={{ color: "var(--text-secondary)" }}>
          {String(row.next_action || "—")}
        </span>
      ),
    },
    {
      key: "created_at",
      label: "Created",
      render: (row: Record<string, unknown>) => (
        <span className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>
          {row.created_at ? new Date(String(row.created_at)).toLocaleDateString() : "—"}
        </span>
      ),
    },
  ];

  return (
    <div className="max-w-6xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Threads</h1>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 rounded text-sm font-medium"
          style={{ backgroundColor: "var(--accent)", color: "#fff" }}
        >
          + Create Thread
        </button>
      </div>

      {error && (
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
          {error}
        </div>
      )}

      <div className="flex gap-3 items-center">
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setOffset(0); }}
          className="px-3 py-2 rounded border text-sm"
          style={inputStyle}
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="completed">Completed</option>
          <option value="blocked">Blocked</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      <div className="rounded-lg border" style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border)" }}>
        <DataTable
          columns={columns}
          rows={items}
          loading={loading}
          emptyMessage="No threads found"
          total={total}
          limit={limit}
          offset={offset}
          onPageChange={setOffset}
          onRowClick={(row) => router.push(`/threads/${row.id}`)}
        />
      </div>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Create Thread">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Title</label>
            <input
              type="text"
              value={createForm.title}
              onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Description</label>
            <textarea
              value={createForm.description}
              onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm h-24"
              style={inputStyle}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Urgency</label>
              <select
                value={createForm.urgency}
                onChange={(e) => setCreateForm({ ...createForm, urgency: e.target.value })}
                className="w-full px-3 py-2 rounded border text-sm"
                style={inputStyle}
              >
                <option value="normal">Normal</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Importance (0-1)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={createForm.importance}
                onChange={(e) => setCreateForm({ ...createForm, importance: e.target.value })}
                className="w-full px-3 py-2 rounded border text-sm"
                style={inputStyle}
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Next Action</label>
            <input
              type="text"
              value={createForm.next_action}
              onChange={(e) => setCreateForm({ ...createForm, next_action: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 rounded text-sm border"
              style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded text-sm font-medium"
              style={{ backgroundColor: "var(--accent)", color: "#fff" }}
            >
              Create
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
