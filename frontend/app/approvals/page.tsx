"use client";

import { useState, useEffect, useCallback } from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { JsonViewer } from "@/components/ui/JsonViewer";
import {
  listPendingApprovals,
  approveProposal,
  rejectProposal,
  deferProposal,
  getFreezeStatus,
  setFreeze,
} from "@/lib/api";

export default function ApprovalsPage() {
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [freezeStatus, setFreezeStatus] = useState<Record<string, unknown> | null>(null);

  // Action modal
  const [actionModal, setActionModal] = useState<{
    open: boolean;
    type: "approve" | "reject" | "defer";
    id: string;
  }>({ open: false, type: "approve", id: "" });
  const [actionNotes, setActionNotes] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [appRes, freezeRes] = await Promise.allSettled([
        listPendingApprovals(),
        getFreezeStatus(),
      ]);
      if (appRes.status === "fulfilled") {
        setItems((appRes.value || []) as Record<string, unknown>[]);
      }
      if (freezeRes.status === "fulfilled") {
        setFreezeStatus(freezeRes.value);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAction = async () => {
    const { type, id } = actionModal;
    try {
      const body = { decision: type === "approve" ? "approved" : type === "reject" ? "rejected" : "deferred", notes: actionNotes };
      if (type === "approve") await approveProposal(id, body);
      else if (type === "reject") await rejectProposal(id, body);
      else await deferProposal(id, body);
      setActionModal({ open: false, type: "approve", id: "" });
      setActionNotes("");
      fetchData();
    } catch (e) {
      setError(String(e));
    }
  };

  const handleFreezeToggle = async () => {
    try {
      const isFrozen = freezeStatus?.frozen || freezeStatus?.is_frozen;
      const reason = isFrozen ? undefined : prompt("Reason for freeze:");
      if (!isFrozen && reason === null) return; // Cancelled
      await setFreeze({ frozen: !isFrozen, reason: reason || undefined });
      const res = await getFreezeStatus();
      setFreezeStatus(res);
    } catch (e) {
      setError(String(e));
    }
  };

  const isFrozen = !!(freezeStatus?.frozen || freezeStatus?.is_frozen);

  if (loading) return <div style={{ color: "var(--text-secondary)" }}>Loading...</div>;

  return (
    <div className="max-w-5xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Approval Queue</h1>
        <div className="flex items-center gap-3">
          {/* Freeze Status */}
          <div className="flex items-center gap-2">
            <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
              Freeze:
            </span>
            <Badge value={isFrozen ? "FROZEN" : "ACTIVE"} />
          </div>
          <button
            onClick={handleFreezeToggle}
            className="px-3 py-1.5 rounded text-sm border"
            style={{
              borderColor: isFrozen ? "#22c55e40" : "#ef444440",
              color: isFrozen ? "#22c55e" : "#ef4444",
            }}
          >
            {isFrozen ? "Unfreeze" : "Freeze"}
          </button>
        </div>
      </div>

      {error && (
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
          {error}
        </div>
      )}

      {/* Freeze details */}
      {isFrozen && freezeStatus?.reason ? (
        <div className="text-sm p-3 rounded" style={{ backgroundColor: "#ef444420", color: "#ef4444" }}>
          Freeze reason: {String(freezeStatus.reason)}
        </div>
      ) : null}

      {/* Pending Items */}
      {items.length === 0 ? (
        <Card>
          <p className="text-sm py-8 text-center" style={{ color: "var(--text-secondary)" }}>
            No pending approval items.
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {items.map((item, i) => (
            <Card key={(item.id as string) || i}>
              <div className="flex items-start justify-between mb-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Badge value={String(item.proposal_type || item.type || "revision")} />
                    <Badge value={String(item.risk_classification || item.risk_class || "")} />
                    <Badge value={String(item.stage || item.status || "pending")} />
                  </div>
                  <h3 className="text-sm font-medium mt-1">
                    {String(item.summary || item.change_summary || item.title || "Revision Proposal")}
                  </h3>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button
                    onClick={() => setActionModal({ open: true, type: "approve", id: String(item.id) })}
                    className="px-3 py-1 rounded text-xs font-medium"
                    style={{ backgroundColor: "#22c55e20", color: "#22c55e" }}
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => setActionModal({ open: true, type: "reject", id: String(item.id) })}
                    className="px-3 py-1 rounded text-xs font-medium"
                    style={{ backgroundColor: "#ef444420", color: "#ef4444" }}
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => setActionModal({ open: true, type: "defer", id: String(item.id) })}
                    className="px-3 py-1 rounded text-xs font-medium"
                    style={{ backgroundColor: "#3b82f620", color: "#3b82f6" }}
                  >
                    Defer
                  </button>
                </div>
              </div>

              {/* Target */}
              {item.target_section ? (
                <p className="text-xs mb-2" style={{ color: "var(--text-secondary)" }}>
                  Target: {String(item.target_section)}
                  {item.target_field ? ` → ${String(item.target_field)}` : ""}
                </p>
              ) : null}

              {/* Evidence count */}
              {(item.evidence_json || item.evidence_links) ? (
                <p className="text-xs mb-2" style={{ color: "var(--text-secondary)" }}>
                  Evidence items: {
                    Array.isArray(item.evidence_json)
                      ? item.evidence_json.length
                      : Array.isArray(item.evidence_links)
                        ? (item.evidence_links as unknown[]).length
                        : "?"
                  }
                </p>
              ) : null}

              {/* Proposed diff */}
              {(item.proposed_diff_json || item.proposed_diff) ? (
                <div className="mt-2">
                  <JsonViewer
                    data={item.proposed_diff_json || item.proposed_diff}
                    collapsed
                    label="Proposed Changes"
                  />
                </div>
              ) : null}

              {/* Evidence detail */}
              {(item.evidence_json || item.evidence_links) ? (
                <div className="mt-2">
                  <JsonViewer
                    data={item.evidence_json || item.evidence_links}
                    collapsed
                    label="Evidence Details"
                  />
                </div>
              ) : null}

              {/* Created */}
              <p className="text-xs mt-2 font-mono" style={{ color: "var(--text-secondary)" }}>
                {item.created_at ? new Date(String(item.created_at)).toLocaleString() : ""}
                {" · "}
                <span>{String(item.id || "").slice(0, 12)}...</span>
              </p>
            </Card>
          ))}
        </div>
      )}

      {/* Action Modal */}
      <Modal
        open={actionModal.open}
        onClose={() => { setActionModal({ open: false, type: "approve", id: "" }); setActionNotes(""); }}
        title={`${actionModal.type.charAt(0).toUpperCase() + actionModal.type.slice(1)} Proposal`}
      >
        <div className="space-y-4">
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            You are about to <strong>{actionModal.type}</strong> this revision proposal.
          </p>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Notes</label>
            <textarea
              value={actionNotes}
              onChange={(e) => setActionNotes(e.target.value)}
              className="w-full px-3 py-2 rounded border text-sm h-24"
              style={{
                backgroundColor: "var(--bg)",
                borderColor: "var(--border)",
                color: "var(--text-primary)",
              }}
              placeholder="Optional notes..."
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => { setActionModal({ open: false, type: "approve", id: "" }); setActionNotes(""); }}
              className="px-4 py-2 rounded text-sm border"
              style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
            >
              Cancel
            </button>
            <button
              onClick={handleAction}
              className="px-4 py-2 rounded text-sm font-medium"
              style={{
                backgroundColor:
                  actionModal.type === "approve" ? "#22c55e" :
                  actionModal.type === "reject" ? "#ef4444" : "#3b82f6",
                color: "#fff",
              }}
            >
              Confirm {actionModal.type}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
