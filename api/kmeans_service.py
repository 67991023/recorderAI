"""K-Means clustering service for RecorderAI.

Fetches recordings from the database, extracts features, and runs
K-Means clustering. Returns results ready for frontend visualization.
"""
import os
from typing import Any, Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor

try:
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


def _get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'recorderai'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123'),
    )


def fetch_recordings() -> List[Dict]:
    """Fetch all recordings from the database."""
    conn = _get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        'SELECT id, text, word_count, character_count, created_at '
        'FROM recordings ORDER BY id'
    )
    recordings = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return recordings


def _determine_n_clusters(n: int) -> int:
    """Choose a sensible number of clusters based on sample count."""
    if n < 4:
        return 2
    if n < 8:
        return 3
    if n < 15:
        return 4
    return min(5, n // 3)


def run_clustering(recordings: List[Dict]) -> Dict[str, Any]:
    """Run K-Means on a list of recording dicts and return visualization data."""
    if not ML_AVAILABLE:
        return {
            "success": False,
            "error": "scikit-learn / numpy not installed in this environment.",
        }

    if len(recordings) < 2:
        return {
            "success": False,
            "error": "Need at least 2 recordings for clustering.",
        }

    # --- Feature matrix: [word_count, character_count] ---
    features = np.array(
        [
            [float(r.get('word_count') or 0), float(r.get('character_count') or 0)]
            for r in recordings
        ]
    )

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    n_clusters = _determine_n_clusters(len(recordings))

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
    labels = kmeans.fit_predict(features_scaled)

    # Silhouette score (requires ≥2 distinct clusters)
    sil_score = 0.0
    if len(set(labels)) > 1:
        try:
            sil_score = float(silhouette_score(features_scaled, labels))
        except Exception:
            pass

    # Cluster centers in original (un-scaled) feature space
    centers = scaler.inverse_transform(kmeans.cluster_centers_).tolist()

    # Build per-point data for the scatter plot
    data_points = []
    for i, r in enumerate(recordings):
        text = r.get('text', '')
        preview = text[:60] + '...' if len(text) > 60 else text
        data_points.append({
            "id": r['id'],
            "label": f"#{r['id']}",
            "text": preview,
            "word_count": int(r.get('word_count') or 0),
            "character_count": int(r.get('character_count') or 0),
            "cluster": int(labels[i]),
        })

    # Per-cluster statistics
    cluster_stats = []
    for c in range(n_clusters):
        pts = [d for d in data_points if d['cluster'] == c]
        avg_wc = float(np.mean([p['word_count'] for p in pts])) if pts else 0.0
        avg_cc = float(np.mean([p['character_count'] for p in pts])) if pts else 0.0
        cluster_stats.append({
            "cluster_id": c,
            "count": len(pts),
            "avg_word_count": round(avg_wc, 1),
            "avg_character_count": round(avg_cc, 1),
            "center_word_count": round(centers[c][0], 1),
            "center_char_count": round(centers[c][1], 1),
        })

    return {
        "success": True,
        "data_points": data_points,
        "cluster_assignments": [int(l) for l in labels],
        "cluster_centers": centers,
        "n_clusters": n_clusters,
        "silhouette_score": round(sil_score, 4),
        "cluster_stats": cluster_stats,
        "total_recordings": len(recordings),
    }


def get_clustering_results() -> Dict[str, Any]:
    """High-level helper: fetch from DB then cluster."""
    try:
        recordings = fetch_recordings()
        return run_clustering(recordings)
    except Exception as exc:
        return {"success": False, "error": str(exc)}
