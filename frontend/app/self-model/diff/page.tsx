"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { JsonViewer } from "@/components/ui/JsonViewer";
import { getSelfModelHistory, computeSelfModelDiff } from "@/lib/api";

export default function SelfModelDiffPage() {
  const router = useRouter();
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fromId, setFromId] = useState("");
  const [toId, setToId] = useState("");
  const [diffResult, setDiffResult] = useState<Record<string, unknown> | null>(null);
  const [diffLoading, setDiffLoading] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const hist = await getSelfModelHistory();
        const items = (hist || []) as Record<string, unknown>[];
        setHistory(items);
        // Auto-select last two if available
        if (items.length >= 2) {
          setFromId(String(items[items.length - 1].id || ""));
          setToId(String(items[0].id || ""));
        }
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleCompare = async () => {
    if (!fromId || !toId) return;
    setDiffLoading(true);
    setError(null);
    try {
      const result = await computeSelfModelDiff({
        from_version_id: fromId,
        to_version_id: toId,
      });
      setDiffResult(result);
    } catch (e) {
      setError(String(e));
    } finally {
      setDiffLoading(false);
    }
  };

  const inputStyle = {
    backgroundColor: "var(--bg)",
    borderColor: "var(--border)",
    color: "var(--text-primary)",
  };

  if (loading) return <div style={{ color: "var(--text-secondary)" }}>Loading...</div>;

  const diffItems = (diffResult?.diff_items || diffResult?.items || []) as Record<string, unknown>[];

  return (
    <div className="max-w-5xl space-y-4">
      <div className="flex items-center gap-3">
        <button onClick={() => router.back()} className="text-sm" style={{ color: "var(--accent)" }}>← Back</button>
        <h1 className="text-2xl font-bold">Self-Model Diff</h1>
      </div>

      {error && (
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
          {error}
        </div>
      )}

      {/* Version Selectors */}
      <Card title="Compare Versions">
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>
              From Version (older)
            </label>
            <select
              value={fromId}
              onChange={(e) => setFromId(e.target.value)}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
            >
              <option value="">Select version...</option>
              {history.map((v) => (
                <option key={String(v.id)} value={String(v.id)}>
                  v{String(v.version_number)} — {v.created_at ? new Date(String(v.created_at)).toLocaleDateString() : ""}
                  {v.change_summary ? ` — ${String(v.change_summary).slice(0, 40)}` : ""}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>
              To Version (newer)
            </label>
            <select
              value={toId}
              onChange={(e) => setToId(e.target.value)}
              className="w-full px-3 py-2 rounded border text-sm"
              style={inputStyle}
            >
              <option value="">Select version...</option>
              {history.map((v) => (
                <option key={String(v.id)} value={String(v.id)}>
                  v{String(v.version_number)} — {v.created_at ? new Date(String(v.created_at)).toLocaleDateString() : ""}
                  {v.change_summary ? ` — ${String(v.change_summary).slice(0, 40)}` : ""}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={handleCompare}
            disabled={!fromId || !toId || diffLoading}
            className="px-4 py-2 rounded text-sm font-medium disabled:opacity-40"
            style={{ backgroundColor: "var(--accent)", color: "#fff" }}
          >
            {diffLoading ? "Computing..." : "Compare"}
          </button>
        </div>
      </Card>

      {/* Diff Results */}
      {diffResult ? (
        <>
          {diffItems.length > 0 ? (
            <div className="space-y-3">
              <h2 className="text-lg font-semibold">
                Changes ({diffItems.length} item{diffItems.length !== 1 ? "s" : ""})
              </h2>
              {diffItems.map((item, i) => (
                <Card key={i}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge value={String(item.category || item.change_type || "")} />
                      <span className="text-sm font-medium">{String(item.section || "")}</span>
                      {item.field ? (
                        <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
                          → {String(item.field)}
                        </span>
                      ) : null}
                    </div>
                  </div>
                  {/* Show the value */}
                  {item.value ? (
                    <div className="mb-2">
                      <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Value</p>
                      <p className="text-sm pl-3" style={{ borderLeft: "2px solid var(--accent)" }}>
                        {typeof item.value === "object" ? JSON.stringify(item.value) : String(item.value)}
                      </p>
                    </div>
                  ) : null}
                  {item.old_value ? (
                    <div className="mb-2">
                      <p className="text-xs mb-1" style={{ color: "#ef4444" }}>Removed</p>
                      <p className="text-sm pl-3" style={{ borderLeft: "2px solid #ef4444" }}>
                        {typeof item.old_value === "object" ? JSON.stringify(item.old_value) : String(item.old_value)}
                      </p>
                    </div>
                  ) : null}
                  {item.new_value ? (
                    <div className="mb-2">
                      <p className="text-xs mb-1" style={{ color: "#22c55e" }}>Added</p>
                      <p className="text-sm pl-3" style={{ borderLeft: "2px solid #22c55e" }}>
                        {typeof item.new_value === "object" ? JSON.stringify(item.new_value) : String(item.new_value)}
                      </p>
                    </div>
                  ) : null}
                  {/* Evidence links */}
                  {item.evidence_links && Array.isArray(item.evidence_links) && (item.evidence_links as unknown[]).length > 0 ? (
                    <div className="mt-2">
                      <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Evidence</p>
                      <div className="flex flex-wrap gap-1">
                        {(item.evidence_links as string[]).map((link, j) => (
                          <code key={j} className="text-xs px-1 py-0.5 rounded" style={{ backgroundColor: "var(--bg)", color: "var(--accent)" }}>
                            {link}
                          </code>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <p className="text-sm py-4 text-center" style={{ color: "var(--text-secondary)" }}>
                No differences found between these versions.
              </p>
            </Card>
          )}

          {/* Raw diff data */}
          <Card title="Raw Diff Response">
            <JsonViewer data={diffResult} collapsed label="Click to expand raw JSON" />
          </Card>
        </>
      ) : null}
    </div>
  );
}
