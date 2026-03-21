"""Demo test data for the RecorderAI clustering dashboard.

Provides pre-computed clustering results that work without a live DB,
allowing immediate demo capability via the /api/demo-clusters endpoint.
"""
from typing import Any, Dict, List

DEMO_RECORDINGS: List[Dict] = [
    {"id": 1,  "text": "สวัสดีครับ ทดสอบระบบบันทึกเสียง",                              "word_count": 4,  "character_count": 30},
    {"id": 2,  "text": "การวิเคราะห์ข้อมูลด้วย Machine Learning และ AI",               "word_count": 7,  "character_count": 48},
    {"id": 3,  "text": "โปรเจคนี้ใช้ Docker Compose สำหรับการ Deploy",                 "word_count": 7,  "character_count": 51},
    {"id": 4,  "text": "K-Means clustering เป็น unsupervised learning algorithm",       "word_count": 6,  "character_count": 55},
    {"id": 5,  "text": "ภาษาไทย Thai NLP tokenization",                                 "word_count": 4,  "character_count": 31},
    {"id": 6,  "text": "การประมวลผลเสียงด้วย Speech-to-Text หรือ STT",                 "word_count": 6,  "character_count": 46},
    {"id": 7,  "text": "Python Flask API backend REST endpoints",                        "word_count": 5,  "character_count": 40},
    {"id": 8,  "text": "PostgreSQL database query optimization index",                   "word_count": 5,  "character_count": 45},
    {"id": 9,  "text": "Docker container deployment production environment nginx",       "word_count": 5,  "character_count": 57},
    {"id": 10, "text": "Silhouette score validation cluster quality measurement metric", "word_count": 7,  "character_count": 63},
    {"id": 11, "text": "สวัสดี",                                                          "word_count": 1,  "character_count": 7},
    {"id": 12, "text": "Chart.js visualization scatter plot cluster colors frontend",   "word_count": 8,  "character_count": 66},
]

# Pre-computed cluster labels (0-indexed) matching DEMO_RECORDINGS order
_DEMO_LABELS = [0, 1, 1, 1, 0, 1, 2, 2, 2, 1, 0, 2]

_DEMO_CENTERS = [[3.0, 22.7], [6.4, 52.6], [5.8, 52.0]]

_DEMO_CLUSTER_STATS = [
    {"cluster_id": 0, "count": 3, "avg_word_count": 3.0,  "avg_character_count": 22.7, "center_word_count": 3.0, "center_char_count": 22.7},
    {"cluster_id": 1, "count": 5, "avg_word_count": 6.4,  "avg_character_count": 52.6, "center_word_count": 6.4, "center_char_count": 52.6},
    {"cluster_id": 2, "count": 4, "avg_word_count": 5.75, "avg_character_count": 52.0, "center_word_count": 5.8, "center_char_count": 52.0},
]


def get_demo_clusters() -> Dict[str, Any]:
    """Return pre-computed demo clustering results for the /api/demo-clusters endpoint."""
    data_points = []
    for i, rec in enumerate(DEMO_RECORDINGS):
        text = rec["text"]
        preview = text[:60] + "..." if len(text) > 60 else text
        data_points.append({
            "id": rec["id"],
            "label": f"#{rec['id']}",
            "text": preview,
            "word_count": rec["word_count"],
            "character_count": rec["character_count"],
            "cluster": _DEMO_LABELS[i],
        })

    return {
        "success": True,
        "data_points": data_points,
        "cluster_assignments": list(_DEMO_LABELS),
        "cluster_centers": _DEMO_CENTERS,
        "n_clusters": 3,
        "silhouette_score": 0.6523,
        "cluster_stats": _DEMO_CLUSTER_STATS,
        "total_recordings": len(DEMO_RECORDINGS),
        "is_demo": True,
    }
