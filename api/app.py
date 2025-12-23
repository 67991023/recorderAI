from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000, debug=True)