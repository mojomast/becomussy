"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { JsonViewer } from "@/components/ui/JsonViewer";
import { getMemory, reinforceMemory, contradictMemory } from "@/lib/api";

export default function MemoryDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [item, setItem] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await getMemory(id);
        setItem(data);
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const handleReinforce = async () => {
    try {
      await reinforceMemory(id);
      setActionMsg("Memory reinforced");
      const data = await getMemory(id);
      setItem(data);
    } catch (e) {
      setError(String(e));
    }
  };

  const handleContradict = async () => {
    const reason = prompt("Reason for contradiction:");
    if (!reason) return;
    try {
      await contradictMemory(id, { contradicted_by: "steward", reason });
      setActionMsg("Contradiction recorded");
      const data = await getMemory(id);
      setItem(data);
    } catch (e) {
      setError(String(e));
    }
  };

  if (loading) {
    return <div style={{ color: "var(--text-secondary)" }}>Loading...</div>;
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
          {error}
        </div>
        <button onClick={() => router.back()} className="text-sm underline" style={{ color: "var(--accent)" }}>
          Go back
        </button>
      </div>
    );
  }

  if (!item) return null;

  return (
    <div className="max-w-4xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="text-sm" style={{ color: "var(--accent)" }}>
            ← Back
          </button>
          <h1 className="text-2xl font-bold">Memory Detail</h1>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleReinforce}
            className="px-3 py-1.5 rounded text-sm border"
            style={{ borderColor: "#22c55e40", color: "#22c55e" }}
          >
            ↑ Reinforce
          </button>
          <button
            onClick={handleContradict}
            className="px-3 py-1.5 rounded text-sm border"
            style={{ borderColor: "#ef444440", color: "#ef4444" }}
          >
            ✗ Contradict
          </button>
        </div>
      </div>

      {actionMsg && (
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#22c55e20", color: "#22c55e" }}>
          {actionMsg}
        </div>
      )}

      {/* Header card */}
      <Card>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Type</p>
            <Badge value={String(item.memory_type || "")} />
          </div>
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Status</p>
            <Badge value={String(item.status || "")} />
          </div>
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Importance</p>
            <span className="font-mono text-sm">{item.importance != null ? Number(item.importance).toFixed(2) : "—"}</span>
          </div>
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Confidence</p>
            <span className="font-mono text-sm">{item.confidence != null ? Number(item.confidence).toFixed(2) : "—"}</span>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Salience</p>
            <span className="font-mono text-sm">{item.salience_score != null ? Number(item.salience_score).toFixed(2) : "—"}</span>
          </div>
          <div>
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Access Count</p>
            <span className="font-mono text-sm">{String(item.access_count ?? "—")}</span>
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

      {/* Summary */}
      {item.summary ? (
        <Card title="Summary">
          <p className="text-sm">{String(item.summary)}</p>
        </Card>
      ) : null}

      {/* Content */}
      <Card title="Content">
        <p className="text-sm whitespace-pre-wrap">{String(item.content || "")}</p>
      </Card>

      {/* Provenance */}
      {item.provenance ? (
        <Card title="Provenance">
          <JsonViewer data={item.provenance} />
        </Card>
      ) : null}

      {/* Metadata */}
      {item.metadata ? (
        <Card title="Metadata">
          <JsonViewer data={item.metadata} />
        </Card>
      ) : null}

      {/* Links */}
      {item.links ? (
        <Card title="Links">
          <JsonViewer data={item.links} />
        </Card>
      ) : null}

      {/* ID */}
      <Card title="Raw ID">
        <code className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>
          {String(item.id || "")}
        </code>
      </Card>
    </div>
  );
}
