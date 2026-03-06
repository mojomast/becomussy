"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { DataTable } from "@/components/ui/DataTable";
import { listProjects, createProject } from "@/lib/api";

export default function ProjectsPage() {
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
    goal: "",
    current_phase: "",
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listProjects({
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
      await createProject({
        title: createForm.title,
        description: createForm.description || undefined,
        goal: createForm.goal || undefined,
        current_phase: createForm.current_phase || undefined,
      });
      setShowCreate(false);
      setCreateForm({ title: "", description: "", goal: "", current_phase: "" });
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
      key: "current_phase",
      label: "Phase",
      render: (row: Record<string, unknown>) => (
        <span className="text-sm" style={{ color: "var(--text-secondary)" }}>
          {String(row.current_phase || "—")}
        </span>
      ),
    },
    {
      key: "goal",
      label: "Goal",
      className: "max-w-xs truncate",
      render: (row: Record<string, unknown>) => (
        <span className="truncate block max-w-xs text-xs" style={{ color: "var(--text-secondary)" }}>
          {String(row.goal || "—")}
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
        <h1 className="text-2xl font-bold">Projects</h1>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 rounded text-sm font-medium"
          style={{ backgroundColor: "var(--accent)", color: "#fff" }}
        >
          + Create Project
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
          <option value="archived">Archived</option>
        </select>
      </div>

      <div className="rounded-lg border" style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border)" }}>
        <DataTable
          columns={columns}
          rows={items}
          loading={loading}
          emptyMessage="No projects found"
          total={total}
          limit={limit}
          offset={offset}
          onPageChange={setOffset}
          onRowClick={(row) => router.push(`/projects/${row.id}`)}
        />
      </div>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Create Project">
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
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Goal</label>
            <input
              type="text"
              value={createForm.goal}
              onChange={(e) => setCreateForm({ ...createForm, goal: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Current Phase</label>
            <input
              type="text"
              value={createForm.current_phase}
              onChange={(e) => setCreateForm({ ...createForm, current_phase: e.target.value })}
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
