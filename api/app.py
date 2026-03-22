from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

from kmeans_service import get_clustering_results, fetch_recordings, run_clustering
from test_data import get_demo_clusters

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'recorderai'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123')
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
    return jsonify({"success": True, "data": [dict(r) for r in recordings], "count": len(recordings)})

@app.route('/api/recordings', methods=['POST'])
def create_recording():
    data = request.get_json()
    text = data.get('text', '')
    word_count = data.get('word_count', 0)
    character_count = len(text)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO recordings (text, word_count, character_count, created_at) VALUES (%s, %s, %s, %s) RETURNING id',
        (text, word_count, character_count, datetime.utcnow())
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
    return jsonify({"success": True, "statistics": dict(stats)})

@app.route('/api/analyze', methods=['POST'])
def analyze_recordings():
    """Submit recordings for K-Means clustering analysis.

    Accepts optional JSON body with a 'recordings' list; if omitted,
    fetches all recordings from the database.
    """
    try:
        body = request.get_json(silent=True) or {}
        recordings = body.get('recordings')

        if recordings is None:
            recordings = fetch_recordings()

        result = run_clustering(recordings)
        status = 200 if result.get('success') else 400
        return jsonify(result), status
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route('/api/analyze-selected', methods=['POST'])
def analyze_selected():
    """Analyze only the recordings whose IDs are passed in the request body.

    Body: { "ids": [1, 3, 5] }
    """
    try:
        body = request.get_json(silent=True) or {}
        ids = body.get('ids', [])
        if not ids:
            return jsonify({"success": False, "error": "No recording IDs provided."}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            'SELECT id, text, word_count, character_count, created_at '
            'FROM recordings WHERE id = ANY(%s) ORDER BY id',
            (ids,)
        )
        recordings = [dict(r) for r in cur.fetchall()]
        cur.close()
        conn.close()

        if not recordings:
            return jsonify({"success": False, "error": "None of the provided IDs were found."}), 404

        result = run_clustering(recordings)
        status = 200 if result.get('success') else 400
        return jsonify(result), status
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route('/api/analyze-all', methods=['POST'])
def analyze_all():
    """Analyze all recordings in the database."""
    try:
        recordings = fetch_recordings()
        result = run_clustering(recordings)
        status = 200 if result.get('success') else 400
        return jsonify(result), status
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route('/api/recordings/<int:recording_id>/analyze', methods=['POST'])
def analyze_single_recording(recording_id):
    """Analyze a single recording by ID (wraps it in a minimal cluster)."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            'SELECT id, text, word_count, character_count, created_at FROM recordings WHERE id = %s',
            (recording_id,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return jsonify({"success": False, "error": f"Recording {recording_id} not found."}), 404

        recording = dict(row)
        return jsonify({
            "success": True,
            "recording": recording,
            "word_count": recording.get('word_count', 0),
            "character_count": recording.get('character_count', 0),
        }), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route('/api/recordings/<int:recording_id>/transcribe', methods=['GET'])
def get_transcription(recording_id):
    """Return the stored text of a recording as its transcription."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT id, text, created_at FROM recordings WHERE id = %s', (recording_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return jsonify({"success": False, "error": f"Recording {recording_id} not found."}), 404

        return jsonify({"success": True, "id": row['id'], "transcription": row['text']}), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    """Get current clustering results with visualization data."""
    try:
        result = get_clustering_results()
        status = 200 if result.get('success') else 400
        return jsonify(result), status
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route('/api/cluster-stats', methods=['GET'])
def get_cluster_stats():
    """Get detailed cluster statistics and metrics."""
    try:
        result = get_clustering_results()
        if not result.get('success'):
            return jsonify(result), 400

        stats_response = {
            "success": True,
            "n_clusters": result["n_clusters"],
            "silhouette_score": result["silhouette_score"],
            "total_recordings": result["total_recordings"],
            "cluster_stats": result["cluster_stats"],
            "cluster_centers": result["cluster_centers"],
        }
        return jsonify(stats_response), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route('/api/demo-clusters', methods=['GET'])
def demo_clusters():
    """Return pre-computed demo clustering results (no DB required)."""
    return jsonify(get_demo_clusters()), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)