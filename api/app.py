from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

app = Flask(__name__)
CORS(app)

# K-Means / TF-IDF configuration
TFIDF_MAX_FEATURES = 100
TFIDF_MIN_DF = 1
TFIDF_MAX_DF = 1.0

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'recorderai'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os. getenv('DB_PASSWORD', 'postgres')
    )
    return conn

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "recorderAI API",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/recordings', methods=['GET'])
def get_recordings():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM recordings ORDER BY created_at DESC LIMIT 50')
    recordings = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"success": True, "data": recordings, "count": len(recordings)})

@app.route('/api/recordings', methods=['POST'])
def create_recording():
    data = request. get_json()
    text = data.get('text', '')
    word_count = data.get('word_count', 0)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO recordings (text, word_count, created_at) VALUES (%s, %s, %s) RETURNING id',
        (text, word_count, datetime.utcnow())
    )
    recording_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"success": True, "id": recording_id, "message": "Recording created"}), 201

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('''
        SELECT 
            COUNT(*) as total_recordings,
            AVG(word_count) as avg_words,
            MAX(word_count) as max_words,
            MIN(word_count) as min_words
        FROM recordings
    ''')
    stats = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"success": True, "statistics": stats})

def run_clustering(recordings):
    """Run K-Means clustering on recordings and return results with 2-D PCA coords."""
    if len(recordings) < 2:
        return {"error": "Need at least 2 recordings for clustering"}

    texts = [r['text'] for r in recordings]

    try:
        vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            min_df=TFIDF_MIN_DF,
            max_df=TFIDF_MAX_DF,
            lowercase=True
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        n_samples = len(texts)
        # Optimal cluster count: 2 for small sets, 3 for medium, up to 4 for large
        if n_samples >= 8:
            n_clusters = min(4, n_samples // 2)
        elif n_samples >= 6:
            n_clusters = 3
        else:
            n_clusters = 2

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
        clusters = kmeans.fit_predict(tfidf_matrix)

        sil_score = 0.0
        if len(set(clusters)) > 1:
            sil_score = float(silhouette_score(tfidf_matrix, clusters))

        dense_matrix = tfidf_matrix.toarray()
        if dense_matrix.shape[1] >= 2:
            pca = PCA(n_components=2, random_state=42)
            coords_2d = pca.fit_transform(dense_matrix)
        else:
            coords_2d = np.zeros((len(texts), 2))

        feature_names = vectorizer.get_feature_names_out()
        cluster_keywords = {}
        for i, center in enumerate(kmeans.cluster_centers_):
            top_indices = center.argsort()[-5:][::-1]
            keywords = [feature_names[idx] for idx in top_indices if center[idx] > 0]
            cluster_keywords[str(i)] = keywords

        points = []
        for idx, rec in enumerate(recordings):
            text_preview = rec['text'][:100] + "..." if len(rec['text']) > 100 else rec['text']
            points.append({
                "id": rec['id'],
                "text": text_preview,
                "cluster": int(clusters[idx]),
                "x": float(coords_2d[idx][0]),
                "y": float(coords_2d[idx][1]),
                "word_count": rec.get('word_count', 0)
            })

        cluster_distribution = {}
        for c in clusters:
            key = str(c)
            cluster_distribution[key] = cluster_distribution.get(key, 0) + 1

        return {
            "n_clusters": n_clusters,
            "n_recordings": len(recordings),
            "silhouette_score": sil_score,
            "cluster_keywords": cluster_keywords,
            "cluster_distribution": cluster_distribution,
            "points": points
        }
    except Exception as e:
        return {"error": str(e)}


@app.route('/api/analyze', methods=['POST'])
def analyze_recording():
    """Save a recording and return its cluster assignment."""
    data = request.get_json()
    text = data.get('text', '')
    word_count = data.get('word_count', len(text.split()))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO recordings (text, word_count, created_at) VALUES (%s, %s, %s) RETURNING id',
        (text, word_count, datetime.utcnow())
    )
    recording_id = cur.fetchone()[0]
    conn.commit()

    cur2 = conn.cursor(cursor_factory=RealDictCursor)
    cur2.execute('SELECT * FROM recordings ORDER BY created_at ASC')
    recordings = cur2.fetchall()
    cur2.close()
    cur.close()
    conn.close()

    cluster_result = run_clustering(recordings)

    return jsonify({
        "success": True,
        "id": recording_id,
        "message": "Recording analyzed",
        "cluster_result": cluster_result
    }), 201


@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    """Return all recordings with their cluster assignments and 2-D PCA coordinates."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM recordings ORDER BY created_at ASC')
    recordings = cur.fetchall()
    cur.close()
    conn.close()

    if not recordings:
        return jsonify({"success": True, "data": None, "message": "No recordings available"})

    cluster_result = run_clustering(recordings)
    return jsonify({"success": True, "data": cluster_result})


@app.route('/api/cluster-stats', methods=['GET'])
def get_cluster_stats():
    """Return per-cluster statistics."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM recordings ORDER BY created_at ASC')
    recordings = cur.fetchall()
    cur.close()
    conn.close()

    if not recordings:
        return jsonify({"success": True, "stats": None, "message": "No recordings available"})

    cluster_result = run_clustering(recordings)

    if "error" in cluster_result:
        return jsonify({"success": False, "error": cluster_result["error"]})

    points = cluster_result["points"]
    cluster_details = {}
    for cluster_id in range(cluster_result["n_clusters"]):
        cluster_points = [p for p in points if p["cluster"] == cluster_id]
        if cluster_points:
            word_counts = [p["word_count"] for p in cluster_points]
            cluster_details[str(cluster_id)] = {
                "count": len(cluster_points),
                "avg_word_count": round(sum(word_counts) / len(word_counts), 1),
                "keywords": cluster_result["cluster_keywords"].get(str(cluster_id), []),
                "recordings": cluster_points
            }

    stats = {
        "total_recordings": len(recordings),
        "n_clusters": cluster_result["n_clusters"],
        "silhouette_score": cluster_result["silhouette_score"],
        "cluster_distribution": cluster_result["cluster_distribution"],
        "cluster_details": cluster_details
    }

    return jsonify({"success": True, "stats": stats})


if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000, debug=True)