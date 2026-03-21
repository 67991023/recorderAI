/**
 * dashboard.js – Tab switching, recordings page, and cluster page logic.
 */

import { getRecordings, createRecording, getStatistics, analyzeClusters, getClusters, getDemoClusters } from './api.js';
import { renderScatterChart, renderDoughnutChart, destroyCharts } from './charts.js';

/* ─────────────────────────────────────────
   Tab navigation
───────────────────────────────────────── */
function initTabs() {
  const tabs  = document.querySelectorAll('.nav-tab');
  const pages = document.querySelectorAll('.page');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t  => t.classList.remove('active'));
      pages.forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const target = document.getElementById(tab.dataset.page);
      if (target) target.classList.add('active');
    });
  });
}

/* ─────────────────────────────────────────
   Recordings page
───────────────────────────────────────── */
async function loadStatistics() {
  try {
    const { statistics } = await getStatistics();
    document.getElementById('totalRecordings').textContent = statistics.total_recordings ?? 0;
    document.getElementById('avgWords').textContent        = Math.round(statistics.avg_words) || 0;
    document.getElementById('maxWords').textContent        = statistics.max_words ?? 0;
    document.getElementById('minWords').textContent        = statistics.min_words ?? 0;
  } catch (err) {
    console.error('Statistics fetch error:', err);
  }
}

async function loadRecordings() {
  const container = document.getElementById('recordingsList');
  try {
    const { data, success } = await getRecordings();
    if (success && data.length > 0) {
      container.innerHTML = data.map(rec => `
        <div class="recording-card">
          <div class="recording-meta">
            ID: ${rec.id} &nbsp;|&nbsp; Words: ${rec.word_count}
            &nbsp;|&nbsp; ${new Date(rec.created_at).toLocaleString()}
          </div>
          <div class="recording-text">${escHtml(rec.text)}</div>
        </div>`).join('');
    } else {
      container.innerHTML = '<p style="text-align:center;color:#777">No recordings yet. Add one above!</p>';
    }
  } catch (err) {
    container.innerHTML = `<div class="alert alert-error">Error loading recordings: ${escHtml(err.message)}</div>`;
  }
}

function initRecordingForm() {
  const form = document.getElementById('recordingForm');
  if (!form) return;

  // Auto-compute word count
  const textInput = document.getElementById('textInput');
  const wcInput   = document.getElementById('wordCount');
  textInput.addEventListener('input', () => {
    wcInput.value = textInput.value.trim().split(/\s+/).filter(Boolean).length;
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn  = form.querySelector('button[type="submit"]');
    const text = textInput.value.trim();
    const wc   = parseInt(wcInput.value, 10) || 0;
    if (!text) return;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Saving…';
    try {
      await createRecording(text, wc);
      form.reset();
      await Promise.all([loadRecordings(), loadStatistics()]);
      showToast('Recording saved!', 'success');
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = '💾 Save Recording';
    }
  });
}

/* ─────────────────────────────────────────
   Clustering page
───────────────────────────────────────── */
let lastClusterResult = null;

async function loadClustering(useDemo = false) {
  const section   = document.getElementById('clusterResults');
  const btnRun    = document.getElementById('btnRunAnalysis');
  const btnDemo   = document.getElementById('btnDemoAnalysis');

  [btnRun, btnDemo].forEach(b => { if (b) b.disabled = true; });
  section.innerHTML = '<div class="loading" style="text-align:center;padding:24px;color:#667eea">⏳ Running K-Means clustering…</div>';

  try {
    const result = useDemo ? await getDemoClusters() : await analyzeClusters();
    if (!result.success) {
      section.innerHTML = `<div class="alert alert-error">${escHtml(result.error)}</div>`;
      return;
    }
    lastClusterResult = result;
    renderClusteringUI(result);
  } catch (err) {
    section.innerHTML = `<div class="alert alert-error">Error: ${escHtml(err.message)}</div>`;
  } finally {
    [btnRun, btnDemo].forEach(b => { if (b) b.disabled = false; });
  }
}

function renderClusteringUI(result) {
  const section = document.getElementById('clusterResults');

  // Demo banner
  const demoBanner = result.is_demo
    ? `<div class="demo-banner">🎬 Demo mode – showing pre-computed sample data</div>`
    : '';

  // Silhouette bar width
  const silW = Math.max(0, Math.min(100, result.silhouette_score * 100)).toFixed(1);

  // Cluster stat cards
  const clusterCards = result.cluster_stats.map(s => `
    <div class="cluster-card c${s.cluster_id}">
      <div class="cluster-title">Cluster ${s.cluster_id}</div>
      <div class="cluster-stat">📊 ${s.count} recordings</div>
      <div class="cluster-stat">📝 Avg words: ${s.avg_word_count}</div>
      <div class="cluster-stat">🔤 Avg chars: ${s.avg_character_count}</div>
    </div>`).join('');

  // Assignment table rows
  const tableRows = result.data_points.map(p => `
    <tr>
      <td>${p.id}</td>
      <td>${escHtml(p.text)}</td>
      <td>${p.word_count}</td>
      <td>${p.character_count}</td>
      <td><span class="badge badge-c${p.cluster}">Cluster ${p.cluster}</span></td>
    </tr>`).join('');

  section.innerHTML = `
    ${demoBanner}

    <!-- KPI row -->
    <div class="stats-grid" style="margin-bottom:20px">
      <div class="stat-card">
        <div class="stat-value">${result.n_clusters}</div>
        <div class="stat-label">Clusters Found</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${result.total_recordings}</div>
        <div class="stat-label">Recordings Analysed</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${(result.silhouette_score * 100).toFixed(1)}%</div>
        <div class="stat-label">Silhouette Score</div>
      </div>
    </div>

    <!-- Silhouette meter -->
    <div class="card" style="padding:16px 20px;margin-bottom:20px">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px">
        <span style="font-weight:600;font-size:0.9rem">Cluster Quality (Silhouette)</span>
        <span style="font-weight:700;color:var(--primary)">${result.silhouette_score.toFixed(4)}</span>
      </div>
      <div class="silhouette-bar-wrap">
        <div class="silhouette-bar" style="width:${silW}%"></div>
      </div>
      <div style="font-size:0.78rem;color:var(--muted);margin-top:4px">
        Score range: −1 (bad) → +1 (perfect). Above 0.5 is considered good.
      </div>
    </div>

    <!-- Cluster stat cards -->
    <div class="cluster-stats-grid">${clusterCards}</div>

    <!-- Charts row -->
    <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:20px">
      <div class="card" style="padding:16px">
        <div class="chart-container"><canvas id="scatterCanvas"></canvas></div>
      </div>
      <div class="card" style="padding:16px">
        <div class="chart-container" style="height:260px"><canvas id="doughnutCanvas"></canvas></div>
      </div>
    </div>

    <!-- Assignment table -->
    <div class="card">
      <div class="section-title">📋 Recording → Cluster Assignments</div>
      <div class="cluster-table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Text</th><th>Words</th><th>Chars</th><th>Cluster</th>
            </tr>
          </thead>
          <tbody>${tableRows}</tbody>
        </table>
      </div>
    </div>`;

  // Render charts after DOM is updated
  destroyCharts();
  requestAnimationFrame(() => {
    const scatterEl  = document.getElementById('scatterCanvas');
    const doughnutEl = document.getElementById('doughnutCanvas');
    if (scatterEl)  renderScatterChart(scatterEl, result);
    if (doughnutEl) renderDoughnutChart(doughnutEl, result.cluster_stats);
  });
}

function initClusteringPage() {
  document.getElementById('btnRunAnalysis')?.addEventListener('click',  () => loadClustering(false));
  document.getElementById('btnDemoAnalysis')?.addEventListener('click', () => loadClustering(true));
}

/* ─────────────────────────────────────────
   Utility helpers
───────────────────────────────────────── */
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function showToast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'error' : 'info'}`;
  el.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:999;max-width:320px;box-shadow:0 4px 16px rgba(0,0,0,.15)';
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

/* ─────────────────────────────────────────
   Boot
───────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initRecordingForm();
  initClusteringPage();

  // Initial data load
  loadStatistics();
  loadRecordings();

  // Refresh recordings every 30 s
  setInterval(() => { loadRecordings(); loadStatistics(); }, 30_000);
});
