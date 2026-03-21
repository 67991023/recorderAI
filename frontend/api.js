/**
 * api.js – lightweight API client for RecorderAI
 */

const API_BASE = '/api';

/**
 * Generic JSON fetch wrapper.
 * Returns parsed JSON or throws an Error with a user-friendly message.
 */
async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const json = await res.json();
  if (!res.ok) {
    throw new Error(json.error || `HTTP ${res.status}`);
  }
  return json;
}

/* ── Recordings ─────────────────────────────────────────────── */

export async function getRecordings() {
  return apiFetch('/recordings');
}

export async function createRecording(text, wordCount) {
  return apiFetch('/recordings', {
    method: 'POST',
    body: JSON.stringify({ text, word_count: wordCount }),
  });
}

export async function getStatistics() {
  return apiFetch('/statistics');
}

/* ── Clustering ──────────────────────────────────────────────── */

export async function analyzeClusters() {
  return apiFetch('/analyze', { method: 'POST', body: JSON.stringify({}) });
}

export async function getClusters() {
  return apiFetch('/clusters');
}

export async function getClusterStats() {
  return apiFetch('/cluster-stats');
}

export async function getDemoClusters() {
  return apiFetch('/demo-clusters');
}
