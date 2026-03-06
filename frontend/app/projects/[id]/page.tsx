"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { JsonViewer } from "@/components/ui/JsonViewer";
import { Modal } from "@/components/ui/Modal";
import { getProject, updateProject, listProjectCommitments, createProjectCommitment } from "@/lib/api";

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [item, setItem] = useState<Record<string, unknown> | null>(null);
  const [commitments, setCommitments] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCommitmentModal, setShowCommitmentModal] = useState(false);
  const [commitForm, setCommitForm] = useState({
    title: "",
    description: "",
    due_date: "",
  });

  useEffect(() => {
    async function load() {
      try {
        const [projData, commitData] = await Promise.all([
          getProject(id),
          listProjectCommitments(id).catch(() => ({ items: [], total: 0 })),
        ]);
        setItem(projData);
        setCommitments((commitData.items || []) as Record<string, unknown>[]);
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const handleCreateCommitment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createProjectCommitment(id, {
        title: commitForm.title,
        description: commitForm.description || undefined,
        due_date: commitForm.due_date || undefined,
      });
      setShowCommitmentModal(false);
      setCommitForm({ title: "", description: "", due_date: "" });
      // Refresh commitments
      const commitData = await listProjectCommitments(id).catch(() => ({ items: [], total: 0 }));
      setCommitments((commitData.items || []) as Record<string, unknown>[]);
    } catch (e) {
      setError(String(e));
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    try {
      const data = await updateProject(id, { status: newStatus });
      setItem(data);
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

  const milestones = item.milestones as unknown[] | undefined;
  const nextSteps = item.next_steps as unknown[] | undefined;

  return (
    <div className="max-w-4xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="text-sm" style={{ color: "var(--accent)" }}>← Back</button>
          <h1 className="text-2xl font-bold">{String(item.title || "Project")}</h1>
        </div>
      </div>

      {/* Project Info */}
      <Card>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Status</p>
            <Badge value={String(item.status || "")} />
          </div>
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Phase</p>
            <span className="text-sm">{String(item.current_phase || "—")}</span>
          </div>
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Created</p>
            <span className="text-xs font-mono">{item.created_at ? new Date(String(item.created_at)).toLocaleString() : "—"}</span>
          </div>
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Updated</p>
            <span className="text-xs font-mono">{item.updated_at ? new Date(String(item.updated_at)).toLocaleString() : "—"}</span>
          </div>
        </div>
        <div className="flex gap-2 mt-2">
          {["active", "paused", "completed", "archived"].map((s) => (
            <button
              key={s}
              onClick={() => handleStatusChange(s)}
              disabled={item.status === s}
              className="px-2 py-1 rounded text-xs border disabled:opacity-30"
              style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
            >
              {s}
            </button>
          ))}
        </div>
      </Card>

      {item.description ? (
        <Card title="Description">
          <p className="text-sm whitespace-pre-wrap">{String(item.description)}</p>
        </Card>
      ) : null}

      {item.goal ? (
        <Card title="Goal">
          <p className="text-sm">{String(item.goal)}</p>
        </Card>
      ) : null}

      {/* Milestones */}
      <Card title="Milestones">
        {milestones && milestones.length > 0 ? (
          <ul className="space-y-2">
            {milestones.map((m, i) => (
              <li key={i} className="text-sm py-1" style={{ borderBottom: "1px solid var(--border)" }}>
                {typeof m === "object" ? JSON.stringify(m) : String(m)}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>No milestones defined</p>
        )}
      </Card>

      {/* Next Steps */}
      <Card title="Next Steps">
        {nextSteps && nextSteps.length > 0 ? (
          <ul className="space-y-2">
            {nextSteps.map((s, i) => (
              <li key={i} className="text-sm py-1" style={{ borderBottom: "1px solid var(--border)" }}>
                {typeof s === "object" ? JSON.stringify(s) : String(s)}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>No next steps defined</p>
        )}
      </Card>

      {/* Commitments */}
      <Card
        title="Commitments"
        action={
          <button
            onClick={() => setShowCommitmentModal(true)}
            className="px-3 py-1 rounded text-xs font-medium"
            style={{ backgroundColor: "var(--accent)", color: "#fff" }}
          >
            + Add Commitment
          </button>
        }
      >
        {commitments.length > 0 ? (
          <div className="space-y-2">
            {commitments.map((c, i) => (
              <div
                key={(c.id as string) || i}
                className="flex items-center justify-between py-2 text-sm"
                style={{ borderBottom: "1px solid var(--border)" }}
              >
                <div>
                  <span className="font-medium">{String(c.title || c.description || "Commitment")}</span>
                  {c.due_date ? (
                    <span className="ml-2 text-xs font-mono" style={{ color: "var(--text-secondary)" }}>
                      Due: {new Date(String(c.due_date)).toLocaleDateString()}
                    </span>
                  ) : null}
                </div>
                <Badge value={String(c.status || "pending")} />
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>No commitments</p>
        )}
      </Card>

      {/* Metadata */}
      {item.metadata ? (
        <Card title="Metadata">
          <JsonViewer data={item.metadata} />
        </Card>
      ) : null}

      <Card title="ID">
        <code className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>{String(item.id || "")}</code>
      </Card>

      {/* Create Commitment Modal */}
      <Modal open={showCommitmentModal} onClose={() => setShowCommitmentModal(false)} title="Add Commitment">
        <form onSubmit={handleCreateCommitment} className="space-y-4">
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Title</label>
            <input
              type="text"
              value={commitForm.title}
              onChange={(e) => setCommitForm({ ...commitForm, title: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Description</label>
            <textarea
              value={commitForm.description}
              onChange={(e) => setCommitForm({ ...commitForm, description: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm h-20"
              style={inputStyle}
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Due Date</label>
            <input
              type="date"
              value={commitForm.due_date}
              onChange={(e) => setCommitForm({ ...commitForm, due_date: e.target.value })}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setShowCommitmentModal(false)}
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
