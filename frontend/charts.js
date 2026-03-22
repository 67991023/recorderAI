/**
 * charts.js – Chart.js helpers for the clustering scatter plot
 * and cluster-size doughnut chart.
 * Updated for dark theme.
 */

// Palette – one colour per cluster (up to 5), matching CSS variables
const CLUSTER_COLORS = [
  { bg: 'rgba(59,130,246,0.75)',   border: '#3b82f6' },  // Blue-500
  { bg: 'rgba(239,68,68,0.75)',    border: '#ef4444' },  // Red-500
  { bg: 'rgba(16,185,129,0.75)',   border: '#10b981' },  // Emerald-500
  { bg: 'rgba(245,158,11,0.75)',   border: '#f59e0b' },  // Amber-500
  { bg: 'rgba(139,92,246,0.75)',   border: '#8b5cf6' },  // Violet-500
];

let scatterChart = null;
let doughnutChart = null;

/**
 * Build Chart.js datasets from clustering result data_points.
 * Groups points by cluster so each cluster has its own colour.
 */
function buildScatterDatasets(dataPoints, nClusters) {
  const datasets = [];
  for (let c = 0; c < nClusters; c++) {
    const pts = dataPoints.filter(p => p.cluster === c);
    const col = CLUSTER_COLORS[c % CLUSTER_COLORS.length];
    datasets.push({
      label: `Cluster ${c} (${pts.length})`,
      data: pts.map(p => ({
        x: p.word_count,
        y: p.character_count,
        meta: p,   // keep for tooltip
      })),
      backgroundColor: col.bg,
      borderColor:     col.border,
      borderWidth: 2,
      pointRadius: 8,
      pointHoverRadius: 11,
    });
  }
  return datasets;
}

/**
 * Render (or update) the scatter chart.
 * @param {HTMLCanvasElement} canvas
 * @param {Object}            clusterResult  – full API response
 */
export function renderScatterChart(canvas, clusterResult) {
  const { data_points, n_clusters, cluster_centers } = clusterResult;
  const datasets = buildScatterDatasets(data_points, n_clusters);

  // Add cluster-center markers
  const centerCol = CLUSTER_COLORS;
  const centerDataset = {
    label: 'Cluster Centers',
    data: cluster_centers.map((c, i) => ({
      x: c[0], y: c[1],
      meta: { text: `Center ${i}`, word_count: c[0].toFixed(1), character_count: c[1].toFixed(1), cluster: i },
    })),
    backgroundColor: cluster_centers.map((_, i) => centerCol[i % centerCol.length].border),
    borderColor: '#fff',
    borderWidth: 3,
    pointRadius: 12,
    pointHoverRadius: 14,
    pointStyle: 'star',
    showLine: false,
  };
  datasets.push(centerDataset);

  if (scatterChart) {
    scatterChart.data.datasets = datasets;
    scatterChart.update();
    return;
  }

  scatterChart = new Chart(canvas.getContext('2d'), {
    type: 'scatter',
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { usePointStyle: true, padding: 16, color: '#f1f5f9' },
        },
        tooltip: {
          callbacks: {
            label(ctx) {
              const { meta } = ctx.raw;
              if (!meta) return '';
              return [
                `  ${meta.text || ''}`,
                `  Words: ${meta.word_count}`,
                `  Chars: ${meta.character_count}`,
              ];
            },
          },
        },
        title: {
          display: true,
          text: 'K-Means Clustering – Word Count vs Character Count',
          font: { size: 14, weight: '600' },
          color: '#f1f5f9',
          padding: { bottom: 12 },
        },
      },
      scales: {
        x: {
          title: { display: true, text: 'Word Count', font: { weight: '600' }, color: '#94a3b8' },
          grid:  { color: 'rgba(255,255,255,0.06)' },
          ticks: { color: '#94a3b8' },
        },
        y: {
          title: { display: true, text: 'Character Count', font: { weight: '600' }, color: '#94a3b8' },
          grid:  { color: 'rgba(255,255,255,0.06)' },
          ticks: { color: '#94a3b8' },
        },
      },
    },
  });
}

/**
 * Render (or update) the cluster-size doughnut chart.
 * @param {HTMLCanvasElement} canvas
 * @param {Array}             clusterStats
 */
export function renderDoughnutChart(canvas, clusterStats) {
  const labels = clusterStats.map(s => `Cluster ${s.cluster_id}`);
  const counts = clusterStats.map(s => s.count);
  const bgColors = clusterStats.map((_, i) => CLUSTER_COLORS[i % CLUSTER_COLORS.length].bg);
  const borderColors = clusterStats.map((_, i) => CLUSTER_COLORS[i % CLUSTER_COLORS.length].border);

  if (doughnutChart) {
    doughnutChart.data.labels = labels;
    doughnutChart.data.datasets[0].data = counts;
    doughnutChart.data.datasets[0].backgroundColor = bgColors;
    doughnutChart.data.datasets[0].borderColor = borderColors;
    doughnutChart.update();
    return;
  }

  doughnutChart = new Chart(canvas.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: counts,
        backgroundColor: bgColors,
        borderColor: borderColors,
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { usePointStyle: true, color: '#f1f5f9' } },
        title: {
          display: true,
          text: 'Cluster Size Distribution',
          font: { size: 13, weight: '600' },
          color: '#f1f5f9',
        },
      },
    },
  });
}

/** Destroy existing charts (call before re-mounting canvases). */
export function destroyCharts() {
  if (scatterChart) { scatterChart.destroy(); scatterChart = null; }
  if (doughnutChart) { doughnutChart.destroy(); doughnutChart = null; }
}
