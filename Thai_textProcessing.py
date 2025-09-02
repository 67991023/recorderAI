"""
Thai text processing and word counting functions
Author: User 67991023
"""

import re
from typing import List, Dict
from collections import Counter
from config import THAI_CONFIG

try:
    import pythainlp
    PYTHAINLP_AVAILABLE = True
except ImportError:
    PYTHAINLP_AVAILABLE = False

def fix_thai_word_count(text: str) -> int:
    """Fix word count for Thai text using proper tokenization"""
    if PYTHAINLP_AVAILABLE:
        try:
            words = pythainlp.word_tokenize(text, engine='newmm')
            valid_words = [word.strip() for word in words if word.strip()]
            return max(1, len(valid_words))
        except Exception:
            pass
    
    thai_chars = len([c for c in text if '\u0E00' <= c <= '\u0E7F'])
    english_words = len([w for w in text.split() if any(c.isalpha() for c in w)])
    
    if thai_chars > 0:
        estimated_thai_words = max(1, thai_chars // 3)
        return estimated_thai_words + english_words
    return max(1, english_words)

def preprocess_text_for_ml(text: str) -> List[str]:
    """Preprocess text for machine learning analysis"""
    try:
        if PYTHAINLP_AVAILABLE:
            tokens = pythainlp.word_tokenize(text, engine='newmm')
        else:
            tokens = []
            words = text.split()
            for word in words:
                if any('\u0E00' <= c <= '\u0E7F' for c in word):
                    subwords = [word[i:i+3] for i in range(0, len(word), 3) if len(word[i:i+3]) >= 2]
                    tokens.extend(subwords)
                else:
                    tokens.append(word)
        
        stop_words = THAI_CONFIG['stop_words']
        filtered_tokens = []
        
        for token in tokens:
            token = token.strip().lower()
            if (token and len(token) > 1 and token not in stop_words and 
                not token.isdigit() and token not in ['', ' ', '\n', '\t'] and len(token) <= 15):
                filtered_tokens.append(token)
        
        return filtered_tokens if filtered_tokens else [text[:10]]
        
    except Exception:
        return [text[:10]] if text else ['default']

def classify_text_by_rules(text: str) -> str:
    """Classify text using rule-based approach"""
    text_lower = text.lower()
    categories = THAI_CONFIG['categories']
    
    category_scores = {}
    for category, keywords in categories.items():
        score = sum(len(keyword) / 3 for keyword in keywords if keyword in text_lower)
        category_scores[category] = score
    
    if category_scores:
        best_category = max(category_scores.items(), key=lambda x: x[1])
        if best_category[1] > 1:
            return best_category[0]
    
    return 'อื่นๆ'

def validate_voice_records(records: List[Dict]) -> List[Dict]:
    """Validate and fix voice records data"""
    validated_records = []
    
    for i, record in enumerate(records):
        if isinstance(record, dict) and 'text' in record:
            if 'word_count' not in record or record['word_count'] <= 0:
                record['word_count'] = fix_thai_word_count(record['text'])
            
            if 'character_count' not in record:
                record['character_count'] = len(record['text'])
            
            if 'id' not in record:
                record['id'] = i + 1
            
            if 'category' not in record:
                record['category'] = classify_text_by_rules(record['text'])
            
            validated_records.append(record)
    
    return validated_records

def clean_text_for_analysis(text: str) -> str:
    """Clean text for analysis purposes"""
    cleaned = re.sub(r'\s+', ' ', text)
    cleaned = re.sub(r'[^\u0E00-\u0E7Fa-zA-Z0-9\s]', '', cleaned)
    return cleaned.strip()

def extract_keywords_from_text(text: str, top_n: int = 10) -> List[str]:
    """Extract keywords from text"""
    tokens = preprocess_text_for_ml(text)
    word_freq = Counter(tokens)
    return [word for word, freq in word_freq.most_common(top_n)]

def calculate_text_complexity(text: str) -> Dict:
    """Calculate text complexity metrics"""
    words = text.split()
    sentences = max(1, len(re.split(r'[.!?。]', text)))
    word_count = len(words)
    avg_word_length = sum(len(word) for word in words) / max(1, word_count) if words else 0
    
    return {
        'word_count': word_count,
        'sentence_count': sentences,
        'avg_words_per_sentence': word_count / sentences,
        'char_count': len(text),
        'avg_word_length': avg_word_length,
        'complexity_score': (word_count / sentences) * avg_word_length
    }