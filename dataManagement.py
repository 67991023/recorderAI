"""
Data Management Functions
========================
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
    directories = [
        FILE_CONFIG['output_dir'],
        FILE_CONFIG['backup_dir']
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Directory ensured: {directory}")

def load_voice_records() -> List[Dict]:
    """
    Load voice records from file
    
    Returns:
        List[Dict]: List of voice records
    """
    data_file = FILE_CONFIG['data_file']
    
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, dict) and 'voice_records' in data:
                voice_records = data['voice_records']
            elif isinstance(data, list):
                voice_records = data
            else:
                voice_records = []
            
            print(f"📁 Loaded {len(voice_records)} voice records")
            return voice_records
            
        except Exception as e:
            print(f"❌ Error loading voice records: {e}")
            return []
    else:
        print("📂 No existing data file found - starting fresh")
        return []

def save_voice_records(voice_records: List[Dict]) -> bool:
    """
    Save voice records to file with backup
    
    Args:
        voice_records: List of voice records to save
        
    Returns:
        bool: Success status
    """
    data_file = FILE_CONFIG['data_file']
    
    try:
        # Create backup if file exists
        if os.path.exists(data_file):
            backup_file = create_backup(data_file)
            print(f"📋 Backup created: {backup_file}")
        
        # Prepare data with metadata
        data = {
            'metadata': {
                'user_id': APP_CONFIG['user_login'],
                'last_updated': APP_CONFIG['current_datetime'],
                'total_records': len(voice_records),
                'version': APP_CONFIG['version'],
                'app_name': APP_CONFIG['app_name']
            },
            'voice_records': voice_records
        }
        
        # Save data
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved {len(voice_records)} voice records")
        return True
        
    except Exception as e:
        print(f"❌ Error saving voice records: {e}")
        return False

def create_backup(file_path: str) -> str:
    """
    Create backup of a file
    
    Args:
        file_path: Path to file to backup
        
    Returns:
        str: Path to backup file
    """
    backup_dir = FILE_CONFIG['backup_dir']
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    
    backup_filename = f"{name}_backup_{timestamp}{ext}"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"⚠️ Backup creation failed: {e}")
        return ""

def validate_voice_record(record: Dict) -> bool:
    """
    Validate a single voice record
    
    Args:
        record: Voice record to validate
        
    Returns:
        bool: Validation status
    """
    required_fields = ['id', 'text', 'timestamp']
    
    if not isinstance(record, dict):
        return False
    
    for field in required_fields:
        if field not in record:
            return False
    
    # Additional validations
    if not record['text'] or not record['text'].strip():
        return False
    
    try:
        datetime.datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
    except:
        return False
    
    return True

def fix_voice_record(record: Dict, record_index: int) -> Dict:
    """
    Fix and enhance a voice record
    
    Args:
        record: Voice record to fix
        record_index: Index for ID assignment
        
    Returns:
        Dict: Fixed voice record
    """
    from text_processing import fix_thai_word_count, classify_text_by_rules
    
    # Ensure required fields
    if 'id' not in record:
        record['id'] = record_index + 1
    
    if 'text' not in record:
        record['text'] = ''
    
    if 'timestamp' not in record:
        record['timestamp'] = datetime.datetime.now().isoformat()
    
    # Fix word count
    if 'word_count' not in record or record['word_count'] <= 0:
        record['word_count'] = fix_thai_word_count(record['text'])
    
    # Fix character count
    if 'character_count' not in record:
        record['character_count'] = len(record['text'])
    
    # Add category if missing
    if 'category' not in record:
        record['category'] = classify_text_by_rules(record['text'])
    
    # Add metadata if missing
    if 'user_id' not in record:
        record['user_id'] = APP_CONFIG['user_login']
    
    if 'version' not in record:
        record['version'] = APP_CONFIG['version']
    
    return record

def cleanup_voice_records(voice_records: List[Dict]) -> List[Dict]:
    """
    Clean up and validate all voice records
    
    Args:
        voice_records: List of voice records
        
    Returns:
        List[Dict]: Cleaned voice records
    """
    cleaned_records = []
    
    for i, record in enumerate(voice_records):
        if validate_voice_record(record):
            fixed_record = fix_voice_record(record, i)
            cleaned_records.append(fixed_record)
        else:
            print(f"⚠️ Skipping invalid record at index {i}")
    
    print(f"🔧 Cleaned {len(cleaned_records)} out of {len(voice_records)} records")
    return cleaned_records

def export_to_csv(voice_records: List[Dict], output_file: str = None) -> str:
    """
    Export voice records to CSV
    
    Args:
        voice_records: List of voice records
        output_file: Output file path
        
    Returns:
        str: Path to exported file
    """
    import pandas as pd
    
    if not voice_records:
        print("❌ No data to export")
        return ""
    
    if not output_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{FILE_CONFIG['output_dir']}/voice_records_export_{timestamp}.csv"
    
    try:
        df = pd.DataFrame(voice_records)
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"📤 Exported {len(voice_records)} records to: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ Export error: {e}")
        return ""

def import_from_csv(csv_file: str) -> List[Dict]:
    """
    Import voice records from CSV
    
    Args:
        csv_file: Path to CSV file
        
    Returns:
        List[Dict]: Imported voice records
    """
    import pandas as pd
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return []
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        voice_records = df.to_dict('records')
        
        # Clean up imported records
        cleaned_records = cleanup_voice_records(voice_records)
        
        print(f"📥 Imported {len(cleaned_records)} records from: {csv_file}")
        return cleaned_records
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return []

def search_voice_records(voice_records: List[Dict], keyword: str, field: str = 'text') -> List[Dict]:
    """
    Search voice records by keyword
    
    Args:
        voice_records: List of voice records
        keyword: Search keyword
        field: Field to search in
        
    Returns:
        List[Dict]: Matching records
    """
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
    """
    Filter voice records by date range
    
    Args:
        voice_records: List of voice records
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        List[Dict]: Filtered records
    """
    if not voice_records:
        return []
    
    filtered_records = []
    
    for record in voice_records:
        if 'date' in record:
            record_date = record['date']
        elif 'timestamp' in record:
            try:
                timestamp = datetime.datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                record_date = timestamp.strftime("%Y-%m-%d")
            except:
                continue
        else:
            continue
        
        # Check date range
        include_record = True
        
        if start_date and record_date < start_date:
            include_record = False
        
        if end_date and record_date > end_date:
            include_record = False
        
        if include_record:
            filtered_records.append(record)
    
    print(f"📅 Filtered to {len(filtered_records)} records between {start_date or 'start'} and {end_date or 'end'}")
    return filtered_records

def get_data_statistics(voice_records: List[Dict]) -> Dict:
    """
    Get basic statistics about the voice records data
    
    Args:
        voice_records: List of voice records
        
    Returns:
        Dict: Data statistics
    """
    if not voice_records:
        return {}
    
    from text_processing import fix_thai_word_count
    
    # Fix word counts if needed
    for record in voice_records:
        if 'word_count' not in record or record['word_count'] <= 0:
            record['word_count'] = fix_thai_word_count(record['text'])
    
    import numpy as np
    
    word_counts = [record['word_count'] for record in voice_records]
    char_counts = [record['character_count'] for record in voice_records if 'character_count' in record]
    
    # Time span
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
    """
    Merge multiple lists of voice records
    
    Args:
        *record_lists: Variable number of record lists
        
    Returns:
        List[Dict]: Merged and deduplicated records
    """
    all_records = []
    seen_texts = set()
    
    for record_list in record_lists:
        for record in record_list:
            # Simple deduplication based on text content
            text_key = record.get('text', '').strip().lower()
            if text_key and text_key not in seen_texts:
                seen_texts.add(text_key)
                all_records.append(record)
    
    # Reassign IDs
    for i, record in enumerate(all_records):
        record['id'] = i + 1
    
    print(f"🔄 Merged to {len(all_records)} unique records")
    return all_records
