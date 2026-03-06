"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { DataTable } from "@/components/ui/DataTable";
import { searchJournal, createJournalEntry } from "@/lib/api";

export default function JournalPage() {
  const router = useRouter();
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 20;
  const [keyword, setKeyword] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({
    entry_type: "reflection",
    title: "",
    content: "",
    tags: "",
    confidence_level: "0.7",
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await searchJournal({
        keyword: keyword || undefined,
        entry_type: typeFilter || undefined,
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
  }, [keyword, typeFilter, offset]);

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
      await createJournalEntry({
        entry_type: createForm.entry_type,
        title: createForm.title || undefined,
        content: createForm.content,
        tags: createForm.tags ? createForm.tags.split(",").map((t) => t.trim()) : undefined,
        confidence_level: parseFloat(createForm.confidence_level),
      });
      setShowCreate(false);
      setCreateForm({
        entry_type: "reflection",
        title: "",
        content: "",
        tags: "",
        confidence_level: "0.7",
      });
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
      key: "entry_type",
      label: "Type",
      render: (row: Record<string, unknown>) => <Badge value={String(row.entry_type || "")} />,
    },
    {
      key: "title",
      label: "Title",
      className: "max-w-xs",
      render: (row: Record<string, unknown>) => (
        <span className="font-medium">{String(row.title || "Untitled")}</span>
      ),
    },
    {
      key: "content",
      label: "Preview",
      className: "max-w-sm truncate",
      render: (row: Record<string, unknown>) => (
        <span className="truncate block max-w-sm text-xs" style={{ color: "var(--text-secondary)" }}>
          {String(row.content || "").slice(0, 120)}
        </span>
      ),
    },
    {
      key: "confidence_level",
      label: "Conf",
      render: (row: Record<string, unknown>) => (
        <span className="font-mono text-xs">
          {row.confidence_level != null ? Number(row.confidence_level).toFixed(2) : "—"}
        </span>
      ),
    },
    {
      key: "created_at",
      label: "Date",
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
        <h1 className="text-2xl font-bold">Journal</h1>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 rounded text-sm font-medium"
          style={{ backgroundColor: "var(--accent)", color: "#fff" }}
        >
          + Create Entry
        </button>
      </div>

      {error && (
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSearch} className="flex gap-3 items-end">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search journal entries..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
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
          <option value="reflection">Reflection</option>
          <option value="observation">Observation</option>
          <option value="decision">Decision</option>
          <option value="synthesis">Synthesis</option>
          <option value="session_end">Session End</option>
        </select>
        <button
          type="submit"
          className="px-4 py-2 rounded text-sm font-medium border"
          style={{ borderColor: "var(--border)", color: "var(--text-primary)" }}
        >
          Search
        </button>
      </form>

      <div className="rounded-lg border" style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border)" }}>
        <DataTable
          columns={columns}
          rows={items}
          loading={loading}
          emptyMessage="No journal entries found"
          total={total}
          limit={limit}
          offset={offset}
          onPageChange={setOffset}
          onRowClick={(row) => router.push(`/journal/${row.id}`)}
        />
      </div>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Create Journal Entry">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Type</label>
            <select
              value={createForm.entry_type}
              onChange={(e) => setCreateForm({ ...createForm, entry_type: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
            >
              <option value="reflection">Reflection</option>
              <option value="observation">Observation</option>
              <option value="decision">Decision</option>
              <option value="synthesis">Synthesis</option>
              <option value="session_end">Session End</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Title</label>
            <input
              type="text"
              value={createForm.title}
              onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Content</label>
            <textarea
              value={createForm.content}
              onChange={(e) => setCreateForm({ ...createForm, content: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm h-32"
              style={inputStyle}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Tags (comma-separated)</label>
              <input
                type="text"
                value={createForm.tags}
                onChange={(e) => setCreateForm({ ...createForm, tags: e.target.value })}
                className="w-full px-3 py-2 rounded border text-sm"
                style={inputStyle}
                placeholder="tag1, tag2"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Confidence (0-1)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={createForm.confidence_level}
                onChange={(e) => setCreateForm({ ...createForm, confidence_level: e.target.value })}
                className="w-full px-3 py-2 rounded border text-sm"
                style={inputStyle}
              />
            </div>
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
