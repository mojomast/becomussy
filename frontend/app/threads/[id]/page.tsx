"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { JsonViewer } from "@/components/ui/JsonViewer";
import { getThread, updateThread } from "@/lib/api";

export default function ThreadDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [item, setItem] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    title: "",
    description: "",
    status: "",
    urgency: "",
    next_action: "",
    blocker: "",
  });

  useEffect(() => {
    async function load() {
      try {
        const data = await getThread(id);
        setItem(data);
        setEditForm({
          title: String(data.title || ""),
          description: String(data.description || ""),
          status: String(data.status || ""),
          urgency: String(data.urgency || ""),
          next_action: String(data.next_action || ""),
          blocker: String(data.blocker || ""),
        });
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const handleSave = async () => {
    try {
      const data = await updateThread(id, {
        title: editForm.title,
        description: editForm.description || undefined,
        status: editForm.status,
        urgency: editForm.urgency,
        next_action: editForm.next_action || undefined,
        blocker: editForm.blocker || undefined,
      });
      setItem(data);
      setEditing(false);
    } catch (e) {
      setError(String(e));
    }
  };

  const inputStyle = {
    backgroundColor: "var(--bg)",
    borderColor: "var(--border)",
    color: "var(--text-primary)",
  };

  if (loading) return <div style={{ color: "var(--text-secondary)" }}>Loading...</div>;
  if (error) {
    return (
      <div className="space-y-4">
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>{error}</div>
        <button onClick={() => router.back()} className="text-sm underline" style={{ color: "var(--accent)" }}>Go back</button>
      </div>
    );
  }
  if (!item) return null;

  return (
    <div className="max-w-4xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="text-sm" style={{ color: "var(--accent)" }}>← Back</button>
          <h1 className="text-2xl font-bold">{String(item.title || "Thread")}</h1>
        </div>
        <button
          onClick={() => setEditing(!editing)}
          className="px-3 py-1.5 rounded text-sm border"
          style={{ borderColor: "var(--border)", color: "var(--text-primary)" }}
        >
          {editing ? "Cancel" : "Edit"}
        </button>
      </div>

      {editing ? (
        <Card title="Edit Thread">
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Title</label>
              <input
                type="text"
                value={editForm.title}
                onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                className="w-full px-3 py-2 rounded border text-sm"
                style={inputStyle}
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Description</label>
              <textarea
                value={editForm.description}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                className="w-full px-3 py-2 rounded border text-sm h-24"
                style={inputStyle}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Status</label>
                <select
                  value={editForm.status}
                  onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                  className="w-full px-3 py-2 rounded border text-sm"
                  style={inputStyle}
                >
                  <option value="active">Active</option>
                  <option value="paused">Paused</option>
                  <option value="completed">Completed</option>
                  <option value="blocked">Blocked</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Urgency</label>
                <select
                  value={editForm.urgency}
                  onChange={(e) => setEditForm({ ...editForm, urgency: e.target.value })}
                  className="w-full px-3 py-2 rounded border text-sm"
                  style={inputStyle}
                >
                  <option value="normal">Normal</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Next Action</label>
              <input
                type="text"
                value={editForm.next_action}
                onChange={(e) => setEditForm({ ...editForm, next_action: e.target.value })}
                className="w-full px-3 py-2 rounded border text-sm"
                style={inputStyle}
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Blocker</label>
              <input
                type="text"
                value={editForm.blocker}
                onChange={(e) => setEditForm({ ...editForm, blocker: e.target.value })}
                className="w-full px-3 py-2 rounded border text-sm"
                style={inputStyle}
              />
            </div>
            <div className="flex justify-end">
              <button
                onClick={handleSave}
                className="px-4 py-2 rounded text-sm font-medium"
                style={{ backgroundColor: "var(--accent)", color: "#fff" }}
              >
                Save Changes
              </button>
            </div>
          </div>
        </Card>
      ) : (
        <>
          <Card>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Status</p>
                <Badge value={String(item.status || "")} />
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Urgency</p>
                <Badge value={String(item.urgency || "normal")} />
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Importance</p>
                <span className="font-mono text-sm">{item.importance != null ? Number(item.importance).toFixed(2) : "—"}</span>
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Created</p>
                <span className="text-xs font-mono">{item.created_at ? new Date(String(item.created_at)).toLocaleString() : "—"}</span>
              </div>
            </div>
          </Card>

          {item.description ? (
            <Card title="Description">
              <p className="text-sm whitespace-pre-wrap">{String(item.description)}</p>
            </Card>
          ) : null}

          {item.next_action ? (
            <Card title="Next Action">
              <p className="text-sm">{String(item.next_action)}</p>
            </Card>
          ) : null}

          {item.blocker ? (
            <Card title="Blocker">
              <p className="text-sm" style={{ color: "#ef4444" }}>{String(item.blocker)}</p>
            </Card>
          ) : null}

          {item.metadata ? (
            <Card title="Metadata">
              <JsonViewer data={item.metadata} />
            </Card>
          ) : null}

          <Card title="ID">
            <code className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>{String(item.id || "")}</code>
          </Card>
        </>
      )}
    </div>
  );
}
