/**
 * charts.js — Chart.js visualisations for the clustering dashboard
 *
 * Requires Chart.js to be loaded globally before this module is imported.
 */

// Cluster colour palette
export const CLUSTER_COLORS = [
    { border: '#667eea', bg: 'rgba(102,126,234,0.75)' },
    { border: '#11998e', bg: 'rgba(17,153,142,0.75)' },
    { border: '#f64f59', bg: 'rgba(246,79,89,0.75)' },
    { border: '#f7b731', bg: 'rgba(247,183,49,0.75)' },
    { border: '#a55eea', bg: 'rgba(165,94,234,0.75)' },
    { border: '#26c6da', bg: 'rgba(38,198,218,0.75)' },
];

export function clusterColor(idx) {
    return CLUSTER_COLORS[idx % CLUSTER_COLORS.length];
}

// ── Scatter plot (PCA 2-D projection) ─────────────────────────────────────────
let scatterChart = null;

export function renderScatterChart(canvasId, points, nClusters) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Group points by cluster
    const datasets = [];
    for (let c = 0; c < nClusters; c++) {
        const clusterPoints = points
            .filter(p => p.cluster === c)
            .map(p => ({ x: p.x, y: p.y, id: p.id, text: p.text }));

        datasets.push({
            label: `Cluster ${c}`,
            data: clusterPoints,
            backgroundColor: clusterColor(c).bg,
            borderColor: clusterColor(c).border,
            borderWidth: 1.5,
            pointRadius: 7,
            pointHoverRadius: 10,
        });
    }

    if (scatterChart) scatterChart.destroy();

    scatterChart = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, padding: 16 } },
                tooltip: {
                    callbacks: {
                        label(item) {
                            const d = item.raw;
                            const preview = d.text ? (d.text.length > 60 ? d.text.slice(0, 60) + '…' : d.text) : '';
                            return [`ID ${d.id}`, preview];
                        },
                    },
                },
            },
            scales: {
                x: { title: { display: true, text: 'PCA Component 1' }, grid: { color: 'rgba(128,128,128,0.1)' } },
                y: { title: { display: true, text: 'PCA Component 2' }, grid: { color: 'rgba(128,128,128,0.1)' } },
            },
        },
    });
}

// ── Cluster distribution bar chart ────────────────────────────────────────────
let distChart = null;

export function renderDistributionChart(canvasId, distribution, nClusters) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = [];
    const values = [];
    const colors = [];

    for (let c = 0; c < nClusters; c++) {
        labels.push(`Cluster ${c}`);
        values.push(distribution[String(c)] || 0);
        colors.push(clusterColor(c).bg);
    }

    if (distChart) distChart.destroy();

    distChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Recordings per Cluster',
                data: values,
                backgroundColor: colors,
                borderColor: colors.map((_, i) => clusterColor(i).border),
                borderWidth: 1.5,
                borderRadius: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y} recordings` } },
            },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: 'rgba(128,128,128,0.1)' } },
            },
        },
    });
}

// ── Destroy both charts (used when switching tabs) ────────────────────────────
export function destroyCharts() {
    if (scatterChart) { scatterChart.destroy(); scatterChart = null; }
    if (distChart)    { distChart.destroy();    distChart    = null; }
}
