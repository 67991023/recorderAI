/**
 * api.js — thin wrapper around the RecorderAI REST endpoints
 */

const API_BASE = '/api';

async function apiFetch(path, options = {}) {
    const res = await fetch(API_BASE + path, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
}

export const api = {
    // ── existing endpoints ──────────────────────────────────────────────
    getRecordings: () => apiFetch('/recordings'),
    getStatistics: () => apiFetch('/statistics'),
    createRecording: (text, wordCount) =>
        apiFetch('/recordings', {
            method: 'POST',
            body: JSON.stringify({ text, word_count: wordCount }),
        }),

    // ── new clustering endpoints ─────────────────────────────────────────
    analyzeRecording: (text, wordCount) =>
        apiFetch('/analyze', {
            method: 'POST',
            body: JSON.stringify({ text, word_count: wordCount }),
        }),
    getClusters: () => apiFetch('/clusters'),
    getClusterStats: () => apiFetch('/cluster-stats'),
};
