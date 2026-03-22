/**
 * dashboard.js – Tab switching, recordings page (with selection + audio/STT),
 * and cluster page logic.
 */

import {
  getRecordings, createRecording, getStatistics,
  analyzeAll, analyzeSelected, getDemoClusters,
} from './api.js';
import { renderScatterChart, renderDoughnutChart, destroyCharts } from './charts.js';
import { AudioRecorder }    from './recorder.js';
import { SpeechTranscriber } from './transcriber.js';

/* ─────────────────────────────────────────
   Selection state – shared between pages
───────────────────────────────────────── */
const selectedIds = new Set();

function updateSelectionUI() {
  const count = selectedIds.size;
  const selCount   = document.getElementById('selectionCount');
  const btnSel     = document.getElementById('btnAnalyzeSelected');
  const btnRunSel  = document.getElementById('btnRunSelected');
  const badge      = document.getElementById('selectedCountBadge');

  if (selCount)  selCount.textContent  = `${count} selected`;
  if (btnSel)    btnSel.disabled       = count === 0;
  if (btnRunSel) btnRunSel.disabled    = count === 0;
  if (badge)     badge.textContent     = count;
}

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
   Recordings page – statistics & list
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
      container.innerHTML = data.map(rec => {
        const isChecked = selectedIds.has(rec.id);
        return `
          <div class="recording-card${isChecked ? ' selected' : ''}" data-id="${rec.id}">
            <input
              type="checkbox"
              class="recording-checkbox"
              data-id="${rec.id}"
              ${isChecked ? 'checked' : ''}
              aria-label="Select recording ${rec.id}"
            />
            <div class="recording-body">
              <div class="recording-meta">
                <span>🆔 ${rec.id}</span>
                <span>📝 ${rec.word_count} words</span>
                <span>🔤 ${rec.character_count ?? '–'} chars</span>
                <span>🕐 ${new Date(rec.created_at).toLocaleString()}</span>
              </div>
              <div class="recording-text">${escHtml(rec.text)}</div>
            </div>
          </div>`;
      }).join('');

      // Attach checkbox listeners
      container.querySelectorAll('.recording-checkbox').forEach(cb => {
        cb.addEventListener('change', () => {
          const id = Number(cb.dataset.id);
          if (cb.checked) selectedIds.add(id);
          else            selectedIds.delete(id);
          cb.closest('.recording-card').classList.toggle('selected', cb.checked);
          updateSelectionUI();
        });
      });
    } else {
      container.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:24px">No recordings yet. Add one above!</p>';
    }
  } catch (err) {
    container.innerHTML = `<div class="alert alert-error">Error loading recordings: ${escHtml(err.message)}</div>`;
  }
}

function initRecordingForm() {
  const form      = document.getElementById('recordingForm');
  const textInput = document.getElementById('textInput');
  const wcInput   = document.getElementById('wordCount');
  const btnClear  = document.getElementById('btnClearForm');

  if (!form) return;

  // Auto-compute word count
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

  btnClear?.addEventListener('click', () => { form.reset(); });
}

/* ─────────────────────────────────────────
   Selection toolbar buttons
───────────────────────────────────────── */
function initSelectionToolbar() {
  document.getElementById('btnSelectAll')?.addEventListener('click', () => {
    document.querySelectorAll('.recording-checkbox').forEach(cb => {
      cb.checked = true;
      selectedIds.add(Number(cb.dataset.id));
      cb.closest('.recording-card').classList.add('selected');
    });
    updateSelectionUI();
  });

  document.getElementById('btnDeselectAll')?.addEventListener('click', () => {
    document.querySelectorAll('.recording-checkbox').forEach(cb => {
      cb.checked = false;
      cb.closest('.recording-card').classList.remove('selected');
    });
    selectedIds.clear();
    updateSelectionUI();
  });

  document.getElementById('btnAnalyzeSelected')?.addEventListener('click', () => {
    if (selectedIds.size === 0) return;
    switchToClusteringAndRun('selected');
  });
}

/* ─────────────────────────────────────────
   Audio recorder
───────────────────────────────────────── */
function initAudioRecorder() {
  const btnStart  = document.getElementById('btnStartRec');
  const btnStop   = document.getElementById('btnStopRec');
  const btnPlay   = document.getElementById('btnPlayRec');
  const waveWrap  = document.getElementById('waveformContainer');
  const canvas    = document.getElementById('waveformCanvas');

  if (!btnStart) return;

  let lastBlob = null;

  const recorder = new AudioRecorder({
    canvas,
    onStop: (blob) => {
      lastBlob = blob;
      btnPlay.disabled = false;
      showToast('Recording stopped. Click ▶ Play to listen.', 'info');
    },
  });

  btnStart.addEventListener('click', async () => {
    try {
      await recorder.start();
      btnStart.disabled = true;
      btnStop.disabled  = false;
      btnPlay.disabled  = true;
      waveWrap.classList.add('visible');
    } catch (err) {
      showToast(`Microphone error: ${err.message}`, 'error');
    }
  });

  btnStop.addEventListener('click', () => {
    recorder.stop();
    btnStart.disabled = false;
    btnStop.disabled  = true;
    waveWrap.classList.remove('visible');
  });

  btnPlay.addEventListener('click', () => {
    if (lastBlob) {
      const url   = URL.createObjectURL(lastBlob);
      const audio = new Audio(url);
      audio.addEventListener('ended', () => URL.revokeObjectURL(url));
      audio.play();
    }
  });
}

/* ─────────────────────────────────────────
   Speech-to-Text
───────────────────────────────────────── */
function initSTT() {
  const btnStart  = document.getElementById('btnStartSTT');
  const btnStop   = document.getElementById('btnStopSTT');
  const langSel   = document.getElementById('sttLang');
  const statusEl  = document.getElementById('sttStatus');
  const textInput = document.getElementById('textInput');
  const wcInput   = document.getElementById('wordCount');

  if (!btnStart) return;

  if (!SpeechTranscriber.isSupported()) {
    btnStart.disabled = true;
    btnStart.title    = 'Speech recognition requires Chrome or Edge';
    showToast('🎤 STT requires Chrome or Edge browser.', 'info');
  }

  let transcriber = null;
  let partialText = '';
  let accumulatedFinal = '';

  const updateTextarea = (partial, isFinal) => {
    if (isFinal) {
      accumulatedFinal += partial + ' ';
      partialText = '';
    } else {
      partialText = partial;
    }
    textInput.value = (accumulatedFinal + partialText).trimStart();
    wcInput.value   = textInput.value.trim().split(/\s+/).filter(Boolean).length;
  };

  btnStart.addEventListener('click', () => {
    accumulatedFinal = textInput.value.trim();
    if (accumulatedFinal) accumulatedFinal += ' ';
    partialText = '';

    try {
      transcriber = new SpeechTranscriber({
        lang: langSel?.value || 'th-TH',
        onResult: (text, isFinal, confidence) => {
          updateTextarea(text, isFinal);
          if (statusEl) {
            const conf = confidence ? ` (${(confidence * 100).toFixed(0)}%)` : '';
            statusEl.style.display = 'block';
            statusEl.textContent   = isFinal
              ? `✅ Transcribed${conf}: "${text}"`
              : `🎙️ Listening: "${text}"`;
          }
        },
        onError: (e) => {
          showToast(`STT error: ${e.error || e.message || 'unknown'}`, 'error');
          btnStart.disabled = false;
          btnStop.disabled  = true;
          if (statusEl) statusEl.style.display = 'none';
        },
        onEnd: () => {
          btnStart.disabled = false;
          btnStop.disabled  = true;
        },
        onStatusChange: (status) => {
          if (statusEl) {
            statusEl.style.display = status === 'listening' ? 'block' : 'none';
            if (status === 'listening') statusEl.textContent = '🎙️ Listening…';
          }
        },
      });

      transcriber.start();
      btnStart.disabled = true;
      btnStop.disabled  = false;
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  btnStop.addEventListener('click', () => {
    transcriber?.stop();
    btnStart.disabled = false;
    btnStop.disabled  = true;
    if (statusEl) statusEl.style.display = 'none';
  });
}

/* ─────────────────────────────────────────
   Clustering page
───────────────────────────────────────── */
let lastClusterResult = null;

function switchToClusteringAndRun(mode = 'all') {
  // Switch tab
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const tab = document.querySelector('[data-page="page-clustering"]');
  if (tab) tab.classList.add('active');
  document.getElementById('page-clustering')?.classList.add('active');

  loadClustering(mode);
}

async function loadClustering(mode = 'all') {
  const section    = document.getElementById('clusterResults');
  const btnAll     = document.getElementById('btnRunAnalysis');
  const btnSel     = document.getElementById('btnRunSelected');
  const btnDemo    = document.getElementById('btnDemoAnalysis');

  [btnAll, btnSel, btnDemo].forEach(b => { if (b) b.disabled = true; });
  section.innerHTML = '<div style="text-align:center;padding:32px;color:var(--text-muted)"><span class="spinner" style="border-color:rgba(59,130,246,.3);border-top-color:#3b82f6;width:24px;height:24px"></span> Running K-Means clustering…</div>';

  try {
    let result;
    if (mode === 'demo') {
      result = await getDemoClusters();
    } else if (mode === 'selected') {
      if (selectedIds.size === 0) {
        section.innerHTML = '<div class="alert alert-info">No recordings selected. Please check the boxes on the Dashboard tab first.</div>';
        return;
      }
      result = await analyzeSelected([...selectedIds]);
    } else {
      result = await analyzeAll();
    }

    if (!result.success) {
      section.innerHTML = `<div class="alert alert-error">${escHtml(result.error)}</div>`;
      return;
    }
    lastClusterResult = result;
    renderClusteringUI(result);
  } catch (err) {
    section.innerHTML = `<div class="alert alert-error">Error: ${escHtml(err.message)}</div>`;
  } finally {
    [btnAll, btnSel, btnDemo].forEach(b => { if (b) b.disabled = false; });
    updateSelectionUI(); // keep selected state in sync
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
        <span style="font-weight:600;font-size:0.9rem;color:var(--text)">Cluster Quality (Silhouette)</span>
        <span style="font-weight:700;color:var(--primary)">${result.silhouette_score.toFixed(4)}</span>
      </div>
      <div class="silhouette-bar-wrap">
        <div class="silhouette-bar" style="width:${silW}%"></div>
      </div>
      <div style="font-size:0.78rem;color:var(--text-muted);margin-top:6px">
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
  document.getElementById('btnRunAnalysis')?.addEventListener('click',  () => loadClustering('all'));
  document.getElementById('btnRunSelected')?.addEventListener('click',  () => loadClustering('selected'));
  document.getElementById('btnDemoAnalysis')?.addEventListener('click', () => loadClustering('demo'));
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
  el.className = `toast alert alert-${type === 'success' ? 'success' : type === 'error' ? 'error' : 'info'}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

/* ─────────────────────────────────────────
   Boot
───────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initRecordingForm();
  initSelectionToolbar();
  initAudioRecorder();
  initSTT();
  initClusteringPage();

  // Initial data load
  loadStatistics();
  loadRecordings();

  // Refresh recordings every 30 s
  setInterval(() => { loadRecordings(); loadStatistics(); }, 30_000);
});
