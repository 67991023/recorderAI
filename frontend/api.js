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

/** Analyze a specific list of recording objects passed directly. */
export async function analyzeRecordings(recordings) {
  return apiFetch('/analyze', {
    method: 'POST',
    body: JSON.stringify({ recordings }),
  });
}

/** Analyze only the recordings whose IDs are in the provided array. */
export async function analyzeSelected(ids) {
  return apiFetch('/analyze-selected', {
    method: 'POST',
    body: JSON.stringify({ ids }),
  });
}

/** Analyze all recordings in the database. */
export async function analyzeAll() {
  return apiFetch('/analyze-all', { method: 'POST', body: JSON.stringify({}) });
}

/** Kept for backward compatibility – maps to analyzeAll. */
export async function analyzeClusters() {
  return analyzeAll();
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

/** Get the transcription text for a single recording by ID. */
export async function getTranscription(recordingId) {
  return apiFetch(`/recordings/${recordingId}/transcribe`);
}

