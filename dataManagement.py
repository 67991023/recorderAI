"""
Data Management Functions
Functions for loading, saving, and managing voice record data
"""

import json
import os
import shutil
from typing import List, Dict, Optional
import datetime
from config import FILE_CONFIG, APP_CONFIG

def create_directories():
    """Create necessary directories"""
    directories = [FILE_CONFIG['output_dir'], FILE_CONFIG['backup_dir']]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Directory ensured: {directory}")

def load_voice_records() -> List[Dict]:
    """Load voice records from JSON file"""
    data_file = FILE_CONFIG['data_file']
    
    if not os.path.exists(data_file):
        print(f"📄 Creating new data file: {data_file}")
        return []
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            voice_records = json.load(f)
        
        if not isinstance(voice_records, list):
            print("⚠️ Invalid data format, creating new list")
            return []
        
        cleaned_records = cleanup_voice_records(voice_records)
        print(f"📂 Loaded {len(cleaned_records)} voice records")
        return cleaned_records
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        backup_file = create_backup(data_file)
        if backup_file:
            print(f"💾 Backup created: {backup_file}")
        return []

def save_voice_records(voice_records: List[Dict]) -> bool:
    """Save voice records to JSON file"""
    if not voice_records:
        print("⚠️ No records to save")
        return False
    
    data_file = FILE_CONFIG['data_file']
    
    try:
        create_backup(data_file)
        cleaned_records = cleanup_voice_records(voice_records)
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_records, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved {len(cleaned_records)} records to {data_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving data: {e}")
        return False

def create_backup(file_path: str) -> str:
    """Create backup of file"""
    if not os.path.exists(file_path):
        return ""
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}_{os.path.basename(file_path)}"
        backup_path = os.path.join(FILE_CONFIG['backup_dir'], backup_name)
        
        os.makedirs(FILE_CONFIG['backup_dir'], exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return backup_path
        
    except Exception as e:
        print(f"⚠️ Backup failed: {e}")
        return ""

def validate_voice_record(record: Dict) -> bool:
    """Validate a voice record"""
    if not isinstance(record, dict):
        return False
    
    required_fields = ['text']
    for field in required_fields:
        if field not in record or not record[field]:
            return False
    
    return True

def fix_voice_record(record: Dict, record_index: int) -> Dict:
    """Fix and enhance a voice record"""
    from Thai_textProcessing import fix_thai_word_count, classify_text_by_rules
    
    if 'id' not in record:
        record['id'] = record_index + 1
    
    if 'text' not in record:
        record['text'] = ''
    
    if 'timestamp' not in record:
        record['timestamp'] = datetime.datetime.now().isoformat()
    
    if 'word_count' not in record or record['word_count'] <= 0:
        record['word_count'] = fix_thai_word_count(record['text'])
    
    if 'character_count' not in record:
        record['character_count'] = len(record['text'])
    
    if 'category' not in record:
        record['category'] = classify_text_by_rules(record['text'])
    
    if 'user_id' not in record:
        record['user_id'] = APP_CONFIG['user_login']
    
    if 'version' not in record:
        record['version'] = APP_CONFIG['version']
    
    return record

def cleanup_voice_records(voice_records: List[Dict]) -> List[Dict]:
    """Clean up and validate voice records"""
    if not voice_records:
        return []
    
    cleaned_records = []
    
    for i, record in enumerate(voice_records):
        if validate_voice_record(record):
            fixed_record = fix_voice_record(record, i)
            cleaned_records.append(fixed_record)
        else:
            print(f"⚠️ Skipping invalid record at index {i}")
    
    return cleaned_records

def export_to_csv(voice_records: List[Dict], output_file: str = None) -> str:
    """Export voice records to CSV"""
    if not voice_records:
        print("❌ No records to export")
        return ""
    
    import pandas as pd
    
    if output_file is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(FILE_CONFIG['output_dir'], f"voice_records_export_{timestamp}.csv")
    
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df = pd.DataFrame(voice_records)
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"📊 Exported {len(voice_records)} records to: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ Export error: {e}")
        return ""

def import_from_csv(csv_file: str) -> List[Dict]:
    """Import voice records from CSV"""
    import pandas as pd
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return []
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        voice_records = df.to_dict('records')
        cleaned_records = cleanup_voice_records(voice_records)
        
        print(f"📥 Imported {len(cleaned_records)} records from: {csv_file}")
        return cleaned_records
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return []

def search_voice_records(voice_records: List[Dict], keyword: str, field: str = 'text') -> List[Dict]:
    """Search voice records by keyword"""
    if not keyword or not voice_records:
        return []
    
    keyword_lower = keyword.lower()
    results = []
    
    for record in voice_records:
        if field in record:
            field_value = str(record[field]).lower()
            if keyword_lower in field_value:
                results.append(record)
    
    print(f"🔍 Found {len(results)} records matching '{keyword}' in field '{field}'")
    return results

def filter_voice_records_by_date(voice_records: List[Dict], start_date: str = None, end_date: str = None) -> List[Dict]:
    """Filter voice records by date range"""
    if not voice_records:
        return []
    
    filtered_records = []
    
    for record in voice_records:
        if 'timestamp' not in record:
            continue
        
        try:
            record_date = datetime.datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')).date()
            
            if start_date and record_date < datetime.datetime.strptime(start_date, "%Y-%m-%d").date():
                continue
            if end_date and record_date > datetime.datetime.strptime(end_date, "%Y-%m-%d").date():
                continue
            
            filtered_records.append(record)
            
        except ValueError:
            continue
    
    print(f"📅 Filtered to {len(filtered_records)} records")
    return filtered_records

def get_data_statistics(voice_records: List[Dict]) -> Dict:
    """Get basic statistics about the voice records data"""
    if not voice_records:
        return {}
    
    from Thai_textProcessing import fix_thai_word_count
    
    for record in voice_records:
        if 'word_count' not in record or record['word_count'] <= 0:
            record['word_count'] = fix_thai_word_count(record['text'])
    
    import numpy as np
    
    word_counts = [record['word_count'] for record in voice_records]
    char_counts = [record['character_count'] for record in voice_records if 'character_count' in record]
    
    timestamps = []
    for record in voice_records:
        if 'timestamp' in record:
            try:
                ts = datetime.datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                timestamps.append(ts)
            except:
                pass
    
    stats = {
        'total_records': len(voice_records),
        'word_statistics': {
            'total_words': sum(word_counts),
            'mean_words': np.mean(word_counts),
            'median_words': np.median(word_counts),
            'std_words': np.std(word_counts),
            'min_words': min(word_counts),
            'max_words': max(word_counts)
        }
    }
    
    if char_counts:
        stats['character_statistics'] = {
            'total_characters': sum(char_counts),
            'mean_characters': np.mean(char_counts),
            'median_characters': np.median(char_counts)
        }
    
    if timestamps:
        stats['time_statistics'] = {
            'first_recording': min(timestamps).isoformat(),
            'last_recording': max(timestamps).isoformat(),
            'time_span_hours': (max(timestamps) - min(timestamps)).total_seconds() / 3600,
            'unique_days': len(set(ts.date() for ts in timestamps))
        }
    
    return stats

def merge_voice_records(*record_lists: List[Dict]) -> List[Dict]:
    """Merge multiple lists of voice records"""
    all_records = []
    seen_texts = set()
    
    for record_list in record_lists:
        for record in record_list:
            text_key = record.get('text', '').strip().lower()
            if text_key and text_key not in seen_texts:
                seen_texts.add(text_key)
                all_records.append(record)
    
    for i, record in enumerate(all_records):
        record['id'] = i + 1
    
    print(f"🔄 Merged to {len(all_records)} unique records")
    return all_records