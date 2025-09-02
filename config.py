"""
Configuration file for Thai Voice Recorder with ML Analytics
===========================================================
Author: User 67991023
Current Date and Time (UTC): 2025-08-28 07:45:12
"""

import os
from typing import Dict, List

# Application Configuration (UPDATED)
APP_CONFIG = {
    'version': 'ml-focused-1.1',
    'app_name': 'Thai Voice Recorder with ML Analytics'
}

# File Configuration
FILE_CONFIG = {
    'data_file': 'voice_records_ml_only.json',
    'output_dir': 'analysis_outputs',
    'backup_dir': 'backups',
    'log_file': 'voice_recorder.log'
}

# Audio Configuration (IMPROVED FOR LONG SENTENCES)
AUDIO_CONFIG = {
    'language': 'th-TH',
    'energy_threshold': 300,
    'pause_threshold': 1.2,  # Increased for longer pauses
    'phrase_threshold': 0.3,
    'timeout': 20,  # Increased timeout
    'phrase_time_limit': 120  # Increased for long sentences
}

# ML Configuration
ML_CONFIG = {
    'max_tfidf_features': 50,
    'min_df': 1,
    'max_df': 0.95,
    'ngram_range': (1, 2),
    'min_clusters': 2,
    'max_clusters': 8,
    'kmeans_n_init': 15,
    'kmeans_max_iter': 400,
    'random_state': 42
}

# Thai Text Processing
THAI_CONFIG = {
    'stop_words': [
        'และ', 'ใน', 'ที่', 'มี', 'เป็น', 'จะ', 'ได้', 'ไม่', 'ของ', 'กับ',
        'แล้ว', 'เมื่อ', 'หรือ', 'ก็', 'ให้', 'มา', 'ไป', 'อยู่', 'คือ', 'นี้',
        'นั้น', 'เขา', 'เธอ', 'มัน', 'พวก', 'บาง', 'ทุก', 'หลาย', 'น้อย'
    ],
    'categories': {
        'การเมือง/ประวัติศาสตร์': [
            'การเมือง', 'ปกครอง', 'กลาง', 'อารยชน', 'เผ่า', 'ก๊ก', 'สงคราม', 
            'อำนาจ', 'ผู้นำ', 'นำ', 'ยอมรับ', 'สถาปนา', 'ดึง', 'กลุ่ม'
        ],
        'สังคม/วัฒนธรรม': [
            'สังคม', 'วัฒนธรรม', 'ชาว', 'คน', 'ชุมชน', 'ประเพณี', 
            'หน่วย', 'ทาง', 'ลักษณะ'
        ],
        'ภูมิศาสตร์/การขยาย': [
            'ยุโรป', 'ขยาย', 'ดินแดน', 'เดินทาง', 'ที่ตั้ง', 'สามารถ', 'ให้'
        ],
        'ความขัดแย้ง/สงคราม': [
            'สงคราม', 'ระหว่าง', 'ลบ', 'กัน', 'เสีย', 'ขึ้น', 'แก่', 'ต่าง'
        ],
        'การศึกษา/ความรู้': [
            'เรียน', 'ศึกษา', 'รู้', 'เข้าใจ', 'วิชา', 'หนังสือ', 'ความรู้'
        ],
        'อื่นๆ': []
    }
}

# Visualization Configuration
VIS_CONFIG = {
    'figure_size': (12, 8),
    'font_size': 10,
    'dpi': 300,
    'colors': {
        'primary': 'skyblue',
        'secondary': 'lightgreen', 
        'accent': 'coral',
        'highlight': 'red'
    },
    'thai_fonts': ['Tahoma', 'Arial Unicode MS', 'DejaVu Sans']
}