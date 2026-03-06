/**
 * becomussy – API client wrapper.
 *
 * All requests go through this helper so we have a single place to set
 * base URL, headers, and error handling.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

interface FetchOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
}

/**
 * Thin wrapper around `fetch` pointed at the becomussy API.
 */
export async function api<T = unknown>(
  path: string,
  options: FetchOptions = {},
): Promise<T> {
  const { body, params, headers: extraHeaders, ...rest } = options;

  // Build URL with query params
  const url = new URL(`${API_BASE}${path}`);
  if (params) {
    for (const [key, val] of Object.entries(params)) {
      if (val !== undefined && val !== "") {
        url.searchParams.set(key, String(val));
      }
    }
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    // MVP header-based auth — steward role
    "X-User-Id": "steward",
    "X-User-Role": "steward",
    ...(extraHeaders as Record<string, string>),
  };

  const response = await fetch(url.toString(), {
    ...rest,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API ${response.status}: ${errorBody}`);
  }

  // 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

// ── Memory ──────────────────────────────────────────────────────────

export function searchMemory(params: {
  q?: string;
  memory_type?: string;
  status?: string;
  limit?: number;
  offset?: number;
}) {
  return api<{ items: unknown[]; total: number }>("/memory/search", { params });
}

export function getMemory(id: string) {
  return api<Record<string, unknown>>(`/memory/${id}`);
}

export function createMemory(body: Record<string, unknown>) {
  return api<Record<string, unknown>>("/memory", { method: "POST", body });
}

export function updateMemory(id: string, body: Record<string, unknown>) {
  return api<Record<string, unknown>>(`/memory/${id}`, { method: "PATCH", body });
}

export function reinforceMemory(id: string) {
  return api(`/memory/${id}/reinforce`, { method: "POST" });
}

export function contradictMemory(id: string, body: { contradicted_by: string; reason: string }) {
  return api(`/memory/${id}/contradict`, { method: "POST", body });
}

// ── Threads ─────────────────────────────────────────────────────────

export function listThreads(params: {
  status?: string;
  limit?: number;
  offset?: number;
}) {
  return api<{ items: unknown[]; total: number }>("/threads", { params });
}

export function getThread(id: string) {
  return api<Record<string, unknown>>(`/threads/${id}`);
}

export function createThread(body: Record<string, unknown>) {
  return api<Record<string, unknown>>("/threads", { method: "POST", body });
}

export function updateThread(id: string, body: Record<string, unknown>) {
  return api<Record<string, unknown>>(`/threads/${id}`, { method: "PATCH", body });
}

// ── Projects ────────────────────────────────────────────────────────

export function listProjects(params: {
  status?: string;
  limit?: number;
  offset?: number;
}) {
  return api<{ items: unknown[]; total: number }>("/projects", { params });
}

export function getProject(id: string) {
  return api<Record<string, unknown>>(`/projects/${id}`);
}

export function createProject(body: Record<string, unknown>) {
  return api<Record<string, unknown>>("/projects", { method: "POST", body });
}

export function updateProject(id: string, body: Record<string, unknown>) {
  return api<Record<string, unknown>>(`/projects/${id}`, { method: "PATCH", body });
}

export function listProjectCommitments(projectId: string) {
  return api<{ items: unknown[]; total: number }>(`/projects/${projectId}/commitments`);
}

export function createProjectCommitment(projectId: string, body: Record<string, unknown>) {
  return api<Record<string, unknown>>(`/projects/${projectId}/commitments`, { method: "POST", body });
}

// ── Commitments ─────────────────────────────────────────────────────

export function listCommitments(params: {
  project_id?: string;
  status?: string;
  overdue?: boolean;
  limit?: number;
  offset?: number;
}) {
  return api<{ items: unknown[]; total: number }>("/commitments", { params });
}

export function getCommitment(id: string) {
  return api<Record<string, unknown>>(`/commitments/${id}`);
}

export function updateCommitment(id: string, body: Record<string, unknown>) {
  return api<Record<string, unknown>>(`/commitments/${id}`, { method: "PATCH", body });
}

// ── Journal ─────────────────────────────────────────────────────────

export function searchJournal(params: {
  keyword?: string;
  entry_type?: string;
  limit?: number;
  offset?: number;
}) {
  return api<{ items: unknown[]; total: number }>("/journal/search", { params });
}

export function getJournalEntry(id: string) {
  return api<Record<string, unknown>>(`/journal/${id}`);
}

export function createJournalEntry(body: Record<string, unknown>) {
  return api<Record<string, unknown>>("/journal", { method: "POST", body });
}

export function updateJournalEntry(id: string, body: Record<string, unknown>) {
  return api<Record<string, unknown>>(`/journal/${id}`, { method: "PATCH", body });
}

export function summarizeJournal(body: { start_date: string; end_date: string }) {
  return api<Record<string, unknown>>("/journal/summarize", { method: "POST", body });
}

// ── Self-Model ──────────────────────────────────────────────────────

export function getCurrentSelfModel() {
  return api<Record<string, unknown>>("/self-model/current");
}

export function getSelfModelHistory() {
  return api<unknown[]>("/self-model/history");
}

export function getSelfModelVersion(id: string) {
  return api<Record<string, unknown>>(`/self-model/version/${id}`);
}

export function createSelfModelVersion(body: Record<string, unknown>) {
  return api<Record<string, unknown>>("/self-model/version", { method: "POST", body });
}

export function computeSelfModelDiff(body: { from_version_id: string; to_version_id: string }) {
  return api<Record<string, unknown>>("/self-model/diff", { method: "POST", body });
}

export function createRevisionProposal(body: Record<string, unknown>) {
  return api<Record<string, unknown>>("/self-model/revision-proposal", { method: "POST", body });
}

// ── Approvals ───────────────────────────────────────────────────────

export function listPendingApprovals() {
  return api<unknown[]>("/approvals/pending");
}

export function approveProposal(id: string, body: { decision: string; notes: string }) {
  return api(`/approvals/${id}/approve`, { method: "POST", body });
}

export function rejectProposal(id: string, body: { decision: string; notes: string }) {
  return api(`/approvals/${id}/reject`, { method: "POST", body });
}

export function deferProposal(id: string, body: { decision: string; notes: string }) {
  return api(`/approvals/${id}/defer`, { method: "POST", body });
}

export function getFreezeStatus() {
  return api<Record<string, unknown>>("/approvals/freeze");
}

export function setFreeze(body: { frozen: boolean; reason?: string }) {
  return api<Record<string, unknown>>("/approvals/freeze", { method: "POST", body });
}

// ── Continuity ──────────────────────────────────────────────────────

export function getResumeBundle(params?: { query?: string; token_budget?: number }) {
  return api<Record<string, unknown>>("/continuity/resume", { params });
}

// ── Audit ───────────────────────────────────────────────────────────

export function listAuditEvents(params: {
  entity_type?: string;
  event_type?: string;
  limit?: number;
  offset?: number;
}) {
  return api<{ items: unknown[]; total: number }>("/audit", { params });
}

export function getAuditEvent(id: string) {
  return api<Record<string, unknown>>(`/audit/${id}`);
}
