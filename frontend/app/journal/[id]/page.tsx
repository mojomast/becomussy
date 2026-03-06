"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { JsonViewer } from "@/components/ui/JsonViewer";
import { getJournalEntry } from "@/lib/api";

export default function JournalDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [item, setItem] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await getJournalEntry(id);
        setItem(data);
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

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

  const tags = (item.tags as string[] | undefined) || [];
  const themes = (item.themes as string[] | undefined) || [];
  const linkedMemories = (item.linked_memory_ids as string[] | undefined) || [];
  const linkedProjects = (item.linked_project_ids as string[] | undefined) || [];

  return (
    <div className="max-w-4xl space-y-4">
      <div className="flex items-center gap-3">
        <button onClick={() => router.back()} className="text-sm" style={{ color: "var(--accent)" }}>← Back</button>
        <h1 className="text-2xl font-bold">{String(item.title || "Journal Entry")}</h1>
      </div>

      {/* Header info */}
      <Card>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Type</p>
            <Badge value={String(item.entry_type || "")} />
          </div>
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Confidence</p>
            <span className="font-mono text-sm">
              {item.confidence_level != null ? Number(item.confidence_level).toFixed(2) : "—"}
            </span>
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
      </Card>

      {/* Content */}
      <Card title="Content">
        <div className="text-sm whitespace-pre-wrap leading-relaxed">
          {String(item.content || "")}
        </div>
      </Card>

      {/* Tags */}
      {tags.length > 0 && (
        <Card title="Tags">
          <div className="flex flex-wrap gap-2">
            {tags.map((tag, i) => (
              <Badge key={i} value={tag} />
            ))}
          </div>
        </Card>
      )}

      {/* Themes */}
      {themes.length > 0 && (
        <Card title="Themes">
          <div className="flex flex-wrap gap-2">
            {themes.map((theme, i) => (
              <Badge key={i} value={theme} />
            ))}
          </div>
        </Card>
      )}

      {/* Linked Memories */}
      {linkedMemories.length > 0 && (
        <Card title="Linked Memories">
          <div className="space-y-1">
            {linkedMemories.map((memId, i) => (
              <a
                key={i}
                href={`/memory/${memId}`}
                className="block text-xs font-mono hover:underline"
                style={{ color: "var(--accent)" }}
              >
                {memId}
              </a>
            ))}
          </div>
        </Card>
      )}

      {/* Linked Projects */}
      {linkedProjects.length > 0 && (
        <Card title="Linked Projects">
          <div className="space-y-1">
            {linkedProjects.map((projId, i) => (
              <a
                key={i}
                href={`/projects/${projId}`}
                className="block text-xs font-mono hover:underline"
                style={{ color: "var(--accent)" }}
              >
                {projId}
              </a>
            ))}
          </div>
        </Card>
      )}

      {/* Follow-up Candidates */}
      {item.follow_up_candidates ? (
        <Card title="Follow-up Candidates">
          <JsonViewer data={item.follow_up_candidates} />
        </Card>
      ) : null}

      {/* Provenance */}
      {item.provenance ? (
        <Card title="Provenance">
          <JsonViewer data={item.provenance} />
        </Card>
      ) : null}

      <Card title="ID">
        <code className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>{String(item.id || "")}</code>
      </Card>
    </div>
  );
}
