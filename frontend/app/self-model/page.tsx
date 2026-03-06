"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { JsonViewer } from "@/components/ui/JsonViewer";
import { getCurrentSelfModel, getSelfModelHistory } from "@/lib/api";

// Renders a single self-model section as organized lists
function SectionView({ title, data }: { title: string; data: Record<string, unknown> | null | undefined }) {
  if (!data || typeof data !== "object") {
    return (
      <Card title={title}>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>No data</p>
      </Card>
    );
  }

  const entries = Object.entries(data);
  if (entries.length === 0) {
    return (
      <Card title={title}>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Empty section</p>
      </Card>
    );
  }

  return (
    <Card title={title}>
      <div className="space-y-3">
        {entries.map(([key, value]) => (
          <div key={key}>
            <p className="text-xs font-medium mb-1 capitalize" style={{ color: "var(--text-secondary)" }}>
              {key.replace(/_/g, " ")}
            </p>
            {Array.isArray(value) ? (
              value.length > 0 ? (
                <ul className="space-y-1">
                  {value.map((item, i) => (
                    <li key={i} className="text-sm pl-3" style={{ borderLeft: "2px solid var(--border)" }}>
                      {typeof item === "object" ? JSON.stringify(item) : String(item)}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs italic" style={{ color: "var(--text-secondary)" }}>empty</p>
              )
            ) : typeof value === "object" && value !== null ? (
              <JsonViewer data={value} />
            ) : (
              <p className="text-sm">{String(value)}</p>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}

export default function SelfModelPage() {
  const router = useRouter();
  const [current, setCurrent] = useState<Record<string, unknown> | null>(null);
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [curr, hist] = await Promise.allSettled([
          getCurrentSelfModel(),
          getSelfModelHistory(),
        ]);
        if (curr.status === "fulfilled") setCurrent(curr.value);
        if (hist.status === "fulfilled") setHistory((hist.value || []) as Record<string, unknown>[]);
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div style={{ color: "var(--text-secondary)" }}>Loading...</div>;

  const sectionNames = ["descriptive", "aspirational", "constrained", "relational"];

  return (
    <div className="max-w-5xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Self-Model</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-4 py-2 rounded text-sm border"
            style={{ borderColor: "var(--border)", color: "var(--text-primary)" }}
          >
            {showHistory ? "Hide History" : "Version History"}
          </button>
          {history.length >= 2 && (
            <button
              onClick={() => router.push("/self-model/diff")}
              className="px-4 py-2 rounded text-sm font-medium"
              style={{ backgroundColor: "var(--accent)", color: "#fff" }}
            >
              Compare Versions
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
          {error}
        </div>
      )}

      {/* Version History Panel */}
      {showHistory && (
        <Card title="Version History">
          {history.length === 0 ? (
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>No version history</p>
          ) : (
            <div className="space-y-2">
              {history.map((v, i) => (
                <div
                  key={(v.id as string) || i}
                  className="flex items-center justify-between py-2 text-sm"
                  style={{ borderBottom: "1px solid var(--border)" }}
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-bold">v{String(v.version_number || i + 1)}</span>
                    <Badge value={String(v.status || v.stage || "")} />
                    {v.change_summary ? (
                      <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
                        {String(v.change_summary).slice(0, 60)}
                      </span>
                    ) : null}
                  </div>
                  <span className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>
                    {v.created_at ? new Date(String(v.created_at)).toLocaleString() : ""}
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Current Self-Model */}
      {current ? (
        <>
          <Card>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Version</p>
                <span className="font-mono font-bold text-lg">v{String(current.version_number || "?")}</span>
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Status</p>
                <Badge value={String(current.status || current.stage || "")} />
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Created</p>
                <span className="text-xs font-mono">{current.created_at ? new Date(String(current.created_at)).toLocaleString() : "—"}</span>
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>ID</p>
                <code className="text-xs font-mono" style={{ color: "var(--text-secondary)" }}>
                  {String(current.id || "").slice(0, 12)}...
                </code>
              </div>
            </div>
          </Card>

          {/* 4 sections */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {sectionNames.map((name) => (
              <SectionView
                key={name}
                title={name.charAt(0).toUpperCase() + name.slice(1)}
                data={current[name] as Record<string, unknown> | null}
              />
            ))}
          </div>

          {/* Change summary */}
          {current.change_summary ? (
            <Card title="Change Summary">
              <p className="text-sm">{String(current.change_summary)}</p>
            </Card>
          ) : null}

          {/* Diff from prior */}
          {current.diff_from_prior_json ? (
            <Card title="Diff from Prior Version">
              <JsonViewer data={current.diff_from_prior_json} collapsed />
            </Card>
          ) : null}

          {/* Full raw data */}
          <Card title="Raw Self-Model Data">
            <JsonViewer data={current} collapsed label="Click to expand raw JSON" />
          </Card>
        </>
      ) : (
        <Card>
          <p className="text-sm py-8 text-center" style={{ color: "var(--text-secondary)" }}>
            No self-model version found. Create the first version to begin.
          </p>
        </Card>
      )}
    </div>
  );
}
