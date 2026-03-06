"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { DataTable } from "@/components/ui/DataTable";
import { searchMemory, createMemory } from "@/lib/api";

export default function MemoryPage() {
  const router = useRouter();
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  // Filters
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  // Create modal
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({
    memory_type: "episodic",
    content: "",
    summary: "",
    importance: "0.5",
    source_context: "",
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await searchMemory({
        q: query || undefined,
        memory_type: typeFilter || undefined,
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
  }, [query, typeFilter, statusFilter, offset]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setOffset(0);
    fetchData();
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createMemory({
        memory_type: createForm.memory_type,
        content: createForm.content,
        summary: createForm.summary || undefined,
        importance: parseFloat(createForm.importance),
        source_context: createForm.source_context || undefined,
      });
      setShowCreate(false);
      setCreateForm({
        memory_type: "episodic",
        content: "",
        summary: "",
        importance: "0.5",
        source_context: "",
      });
      fetchData();
    } catch (e) {
      setError(String(e));
    }
  };

  const columns = [
    {
      key: "memory_type",
      label: "Type",
      render: (row: Record<string, unknown>) => <Badge value={String(row.memory_type || "")} />,
    },
    {
      key: "summary",
      label: "Summary",
      className: "max-w-xs truncate",
      render: (row: Record<string, unknown>) => (
        <span className="truncate block max-w-xs">
          {String(row.summary || row.content || "").slice(0, 100)}
        </span>
      ),
    },
    {
      key: "importance",
      label: "Imp",
      render: (row: Record<string, unknown>) => (
        <span className="font-mono text-xs">{row.importance != null ? Number(row.importance).toFixed(2) : "—"}</span>
      ),
    },
    {
      key: "salience_score",
      label: "Sal",
      render: (row: Record<string, unknown>) => (
        <span className="font-mono text-xs">{row.salience_score != null ? Number(row.salience_score).toFixed(2) : "—"}</span>
      ),
    },
    {
      key: "confidence",
      label: "Conf",
      render: (row: Record<string, unknown>) => (
        <span className="font-mono text-xs">{row.confidence != null ? Number(row.confidence).toFixed(2) : "—"}</span>
      ),
    },
    {
      key: "status",
      label: "Status",
      render: (row: Record<string, unknown>) => <Badge value={String(row.status || "")} />,
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

  const inputStyle = {
    backgroundColor: "var(--bg)",
    borderColor: "var(--border)",
    color: "var(--text-primary)",
  };

  return (
    <div className="max-w-6xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Memory Explorer</h1>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 rounded text-sm font-medium"
          style={{ backgroundColor: "var(--accent)", color: "#fff" }}
        >
          + Create Memory
        </button>
      </div>

      {error && (
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
          {error}
        </div>
      )}

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-3 items-end">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search memories..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full px-3 py-2 rounded border text-sm"
            style={inputStyle}
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => { setTypeFilter(e.target.value); setOffset(0); }}
          className="px-3 py-2 rounded border text-sm"
          style={inputStyle}
        >
          <option value="">All Types</option>
          <option value="episodic">Episodic</option>
          <option value="semantic">Semantic</option>
          <option value="procedural">Procedural</option>
          <option value="working">Working</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setOffset(0); }}
          className="px-3 py-2 rounded border text-sm"
          style={inputStyle}
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="archived">Archived</option>
          <option value="deprecated">Deprecated</option>
        </select>
        <button
          type="submit"
          className="px-4 py-2 rounded text-sm font-medium border"
          style={{ borderColor: "var(--border)", color: "var(--text-primary)" }}
        >
          Search
        </button>
      </form>

      {/* Results Table */}
      <div className="rounded-lg border" style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border)" }}>
        <DataTable
          columns={columns}
          rows={items}
          loading={loading}
          emptyMessage="No memory items found"
          total={total}
          limit={limit}
          offset={offset}
          onPageChange={setOffset}
          onRowClick={(row) => router.push(`/memory/${row.id}`)}
        />
      </div>

      {/* Create Modal */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Create Memory">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Type</label>
            <select
              value={createForm.memory_type}
              onChange={(e) => setCreateForm({ ...createForm, memory_type: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
            >
              <option value="episodic">Episodic</option>
              <option value="semantic">Semantic</option>
              <option value="procedural">Procedural</option>
              <option value="working">Working</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Content</label>
            <textarea
              value={createForm.content}
              onChange={(e) => setCreateForm({ ...createForm, content: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm h-24"
              style={inputStyle}
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Summary</label>
            <input
              type="text"
              value={createForm.summary}
              onChange={(e) => setCreateForm({ ...createForm, summary: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>
              Importance (0-1)
            </label>
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
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>
              Source Context
            </label>
            <input
              type="text"
              value={createForm.source_context}
              onChange={(e) => setCreateForm({ ...createForm, source_context: e.target.value })}
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
