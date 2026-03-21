/**
 * dashboard.js — wires the RecorderAI dashboard UI together
 */

import { api } from './api.js';
import { renderScatterChart, renderDistributionChart, clusterColor, destroyCharts } from './charts.js';

// ── Toast ───────────────────────────────────────────────────────────────────
function showToast(msg, type = 'info') {
    const container = document.getElementById('toastContainer');
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = msg;
    container.appendChild(el);
    setTimeout(() => el.remove(), 3300);
}

// ── Tab switching ────────────────────────────────────────────────────────────
function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            const panel = document.getElementById(btn.dataset.tab);
            if (panel) panel.classList.add('active');
        });
    });
}

// ── Dark-mode toggle ─────────────────────────────────────────────────────────
function initTheme() {
    const btn = document.getElementById('darkToggle');
    const saved = localStorage.getItem('theme') || 'light';
    applyTheme(saved);
    btn.addEventListener('click', () => {
        const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        localStorage.setItem('theme', next);
    });
}

function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    document.getElementById('darkToggle').textContent = theme === 'dark' ? '☀️' : '🌙';
}

// ── Statistics tab ────────────────────────────────────────────────────────────
async function loadStatistics() {
    try {
        const { statistics: s } = await api.getStatistics();
        document.getElementById('statTotal').textContent   = s.total_recordings  ?? 0;
        document.getElementById('statAvg').textContent     = Math.round(s.avg_words  ?? 0);
        document.getElementById('statMax').textContent     = s.max_words  ?? 0;
        document.getElementById('statMin').textContent     = s.min_words  ?? 0;
    } catch (e) {
        console.error('Statistics error', e);
    }
}

// ── Recordings tab ────────────────────────────────────────────────────────────
let allRecordingPoints = [];   // cache last cluster points for badge colours

async function loadRecordings() {
    const container = document.getElementById('recordingsList');
    container.innerHTML = loadingHTML('Loading recordings…');
    try {
        const { data, success } = await api.getRecordings();
        if (!success || !data || data.length === 0) {
            container.innerHTML = emptyHTML('📭', 'No recordings yet', 'Add your first recording below.');
            return;
        }

        // Also fetch cluster assignments if available
        let pointMap = {};
        try {
            const res = await api.getClusters();
            if (res.success && res.data && res.data.points) {
                res.data.points.forEach(p => { pointMap[p.id] = p.cluster; });
                allRecordingPoints = res.data.points;
            }
        } catch (_) { /* clustering may not have enough data yet */ }

        container.innerHTML = '';
        data.forEach(rec => {
            const clusterIdx = pointMap[rec.id];
            const badge = clusterIdx !== undefined
                ? `<span class="cluster-badge" style="background:${clusterColor(clusterIdx).border}">Cluster ${clusterIdx}</span>`
                : '';
            const card = document.createElement('div');
            card.className = 'recording-card';
            card.innerHTML = `
                <div class="recording-meta">
                    <span>ID: ${rec.id}</span>
                    <span>Words: ${rec.word_count}</span>
                    <span>${new Date(rec.created_at).toLocaleString()}</span>
                    ${badge}
                </div>
                <div class="recording-text">${escapeHtml(rec.text)}</div>
            `;
            container.appendChild(card);
        });
    } catch (e) {
        container.innerHTML = `<div class="state-box"><div class="state-icon">⚠️</div><div class="state-title">Error loading recordings</div><div class="state-sub">${e.message}</div></div>`;
    }
}

// ── Add Recording form ────────────────────────────────────────────────────────
function initRecordingForm() {
    const textArea = document.getElementById('recordText');
    const wcInput  = document.getElementById('recordWordCount');
    const wcHint   = document.getElementById('wcHint');

    textArea.addEventListener('input', () => {
        const trimmed = textArea.value.trim();
        const words = trimmed === '' ? 0 : trimmed.split(/\s+/).length;
        wcInput.value = words;
        wcHint.textContent = `${words} word${words !== 1 ? 's' : ''} counted`;
    });

    document.getElementById('recordingForm').addEventListener('submit', async e => {
        e.preventDefault();
        const text      = textArea.value.trim();
        const wordCount = parseInt(wcInput.value) || 0;
        if (!text) { showToast('Please enter some text.', 'error'); return; }

        const btn = e.target.querySelector('[type="submit"]');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;display:inline-block;vertical-align:middle;margin:0 6px 0 0"></span>Analyzing…';

        try {
            const result = await api.analyzeRecording(text, wordCount);
            showToast(`Saved (ID ${result.id}) and analyzed!`, 'success');
            textArea.value = '';
            wcInput.value  = '';
            wcHint.textContent = '';
            await loadStatistics();
            await loadRecordings();
            // Refresh clustering panel silently
            refreshClusteringPanel();
        } catch (err) {
            showToast('Error: ' + err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '🚀 Analyze & Save';
        }
    });
}

// ── Clustering Analysis tab ────────────────────────────────────────────────────
let activeFilter = 'all';

async function loadClusteringPanel() {
    const statsEl = document.getElementById('clusterSummary');
    statsEl.innerHTML = loadingHTML('Running K-Means analysis…');

    try {
        const [clustersRes, statsRes] = await Promise.all([
            api.getClusters(),
            api.getClusterStats(),
        ]);

        if (!clustersRes.success || !clustersRes.data) {
            statsEl.innerHTML = emptyHTML('🤖', 'Not enough data', 'Add at least 2 recordings to run clustering.');
            destroyCharts();
            return;
        }

        const data  = clustersRes.data;
        const stats = statsRes.success ? statsRes.stats : null;

        // Silhouette score badge
        const sil = data.silhouette_score;
        const silClass = sil >= 0.5 ? 'good' : sil >= 0.25 ? 'ok' : 'low';
        const silLabel  = sil >= 0.5 ? '✅ Good' : sil >= 0.25 ? '⚠️ Fair' : '🔴 Weak';

        // Summary card
        statsEl.innerHTML = `
            <div class="stats-grid" style="margin-bottom:0">
                <div class="stat-card">
                    <div class="stat-icon purple">🔢</div>
                    <div class="stat-info">
                        <div class="stat-value">${data.n_clusters}</div>
                        <div class="stat-label">Clusters</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon green">📝</div>
                    <div class="stat-info">
                        <div class="stat-value">${data.n_recordings}</div>
                        <div class="stat-label">Recordings Analyzed</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon blue">📊</div>
                    <div class="stat-info">
                        <div class="stat-value">${sil.toFixed(3)}</div>
                        <div class="stat-label">Silhouette Score</div>
                    </div>
                </div>
            </div>
            <div style="margin-top:12px">
                <span class="score-badge ${silClass}">${silLabel} separation quality</span>
            </div>
        `;

        // Charts
        renderScatterChart('chartScatter', data.points, data.n_clusters);
        renderDistributionChart('chartDist', data.cluster_distribution, data.n_clusters);

        // Keyword table
        renderKeywordTable(data.cluster_keywords, data.n_clusters, stats);

        // Cluster detail filter chips
        renderFilterChips(data.n_clusters, data.points);

    } catch (e) {
        statsEl.innerHTML = `<div class="state-box"><div class="state-icon">⚠️</div><div class="state-title">Analysis error</div><div class="state-sub">${e.message}</div></div>`;
    }
}

function refreshClusteringPanel() {
    // Only refresh if the clustering tab is currently active
    const panel = document.getElementById('tab-clustering');
    if (panel && panel.classList.contains('active')) {
        loadClusteringPanel();
    }
}

function renderKeywordTable(keywords, nClusters, stats) {
    const tbody = document.getElementById('clusterTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    for (let c = 0; c < nClusters; c++) {
        const kws   = (keywords[String(c)] || []).join(', ') || '—';
        const detail = stats && stats.cluster_details[String(c)];
        const count = detail ? detail.count : '—';
        const avg   = detail ? detail.avg_word_count : '—';
        const color = clusterColor(c).border;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="cluster-badge" style="background:${color}">Cluster ${c}</span></td>
            <td>${count}</td>
            <td>${avg}</td>
            <td style="max-width:280px;word-break:break-word">${kws}</td>
        `;
        tbody.appendChild(tr);
    }
}

function renderFilterChips(nClusters, points) {
    const row = document.getElementById('filterRow');
    if (!row) return;
    row.innerHTML = '<span class="filter-label">Filter by cluster:</span>';

    const allChip = document.createElement('button');
    allChip.className = `filter-chip ${activeFilter === 'all' ? 'active' : ''}`;
    allChip.textContent = 'All';
    allChip.addEventListener('click', () => applyFilter('all', points, nClusters));
    row.appendChild(allChip);

    for (let c = 0; c < nClusters; c++) {
        const chip = document.createElement('button');
        chip.className = `filter-chip ${activeFilter === c ? 'active' : ''}`;
        chip.textContent = `Cluster ${c}`;
        chip.style.borderColor = clusterColor(c).border;
        chip.addEventListener('click', () => applyFilter(c, points, nClusters));
        row.appendChild(chip);
    }

    renderFilteredPoints(points, activeFilter, nClusters);
}

function applyFilter(value, points, nClusters) {
    activeFilter = value;
    document.querySelectorAll('.filter-chip').forEach((chip, idx) => {
        chip.classList.toggle('active', idx === 0 ? value === 'all' : value === idx - 1);
    });
    renderFilteredPoints(points, value, nClusters);
}

function renderFilteredPoints(points, filter, nClusters) {
    const container = document.getElementById('filteredRecordings');
    if (!container) return;
    const filtered = filter === 'all' ? points : points.filter(p => p.cluster === filter);
    if (!filtered.length) {
        container.innerHTML = emptyHTML('🔍', 'No results', 'Try a different filter.');
        return;
    }
    container.innerHTML = filtered.map(p => {
        const color = clusterColor(p.cluster).border;
        return `
            <div class="recording-card">
                <div class="recording-meta">
                    <span>ID: ${p.id}</span>
                    <span>Words: ${p.word_count}</span>
                    <span class="cluster-badge" style="background:${color}">Cluster ${p.cluster}</span>
                    <span style="font-size:0.78rem;color:var(--text-secondary)">PCA: (${p.x.toFixed(3)}, ${p.y.toFixed(3)})</span>
                </div>
                <div class="recording-text">${escapeHtml(p.text)}</div>
            </div>
        `;
    }).join('');
}

// ── Utility helpers ────────────────────────────────────────────────────────────
function loadingHTML(msg = 'Loading…') {
    return `<div class="state-box"><div class="spinner"></div><div class="state-sub">${msg}</div></div>`;
}

function emptyHTML(icon, title, sub) {
    return `<div class="state-box"><div class="state-icon">${icon}</div><div class="state-title">${title}</div><div class="state-sub">${sub}</div></div>`;
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// ── Boot ──────────────────────────────────────────────────────────────────────
async function init() {
    initTheme();
    initTabs();
    initRecordingForm();

    // Tab-change handler to (re)load clustering data lazily
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.dataset.tab === 'tab-clustering') loadClusteringPanel();
            if (btn.dataset.tab === 'tab-recordings') loadRecordings();
        });
    });

    // Initial data load
    await Promise.all([loadStatistics(), loadRecordings()]);

    // Expose reload helper for the Refresh button used in index.html
    window._reloadRecordings = loadRecordings;

    // Auto-refresh every 30 s
    setInterval(async () => {
        await loadStatistics();
        if (document.getElementById('tab-recordings').classList.contains('active')) {
            loadRecordings();
        }
    }, 30000);
}

document.addEventListener('DOMContentLoaded', init);
