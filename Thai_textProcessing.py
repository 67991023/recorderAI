import re
from typing import List, Dict
from config import THAI_CONFIG

# Check for Thai NLP availability
try:
    import pythainlp
    PYTHAINLP_AVAILABLE = True
except ImportError:
    PYTHAINLP_AVAILABLE = False

def fix_thai_word_count(text: str) -> int:
    if PYTHAINLP_AVAILABLE:
        try:
            words = pythainlp.word_tokenize(text, engine='newmm')
            valid_words = [word.strip() for word in words if word.strip() and len(word.strip()) > 0]
            return max(1, len(valid_words))
        except Exception as e:
            print(f"⚠️ Thai tokenization error: {e}")
    
    thai_chars = len([c for c in text if '\u0E00' <= c <= '\u0E7F'])
    english_words = len([w for w in text.split() if any(c.isalpha() for c in w)])
    
    if thai_chars > 0:
        estimated_thai_words = max(1, thai_chars // 3)
        return estimated_thai_words + english_words
    else:
        return max(1, english_words)

def preprocess_text_for_ml(text: str) -> List[str]:
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
            if (token and 
                len(token) > 1 and 
                token not in stop_words and 
                not token.isdigit() and
                not token in ['', ' ', '\n', '\t'] and
                len(token) <= 15):
                filtered_tokens.append(token)
        
        return filtered_tokens if filtered_tokens else [text[:10]]
        
    except Exception as e:
        print(f"⚠️ Text preprocessing error: {e}")
        return [text[:10]] if text else ['default']

def classify_text_by_rules(text: str) -> str:
    text_lower = text.lower()
    categories = THAI_CONFIG['categories']
    
    category_scores = {}
    for category, keywords in categories.items():
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                # Weight longer keywords more
                score += len(keyword) / 3
        category_scores[category] = score
    
    # Find best category
    if category_scores:
        best_category = max(category_scores.items(), key=lambda x: x[1])
        if best_category[1] > 1:  # Minimum threshold
            return best_category[0]
    
    return 'อื่นๆ'

def validate_voice_records(records: List[Dict]) -> List[Dict]:
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
    cleaned = re.sub(r'\s+', ' ', text)
    cleaned = re.sub(r'[^\u0E00-\u0E7Fa-zA-Z0-9\s]', '', cleaned)
    
    return cleaned.strip()

def extract_keywords_from_text(text: str, top_n: int = 10) -> List[str]:
    tokens = preprocess_text_for_ml(text)
    
    from collections import Counter
    word_freq = Counter(tokens)
    
    top_keywords = [word for word, freq in word_freq.most_common(top_n)]
    
    return top_keywords

def calculate_text_complexity(text: str) -> Dict:
    words = text.split()
    sentences = len(re.split(r'[.!?。]', text))
    
    metrics = {
        'word_count': len(words),
        'sentence_count': max(1, sentences),
        'avg_words_per_sentence': len(words) / max(1, sentences),
        'char_count': len(text),
        'avg_word_length': sum(len(word) for word in words) / max(1, len(words)),
        'complexity_score': len(words) / max(1, sentences) * (sum(len(word) for word in words) / max(1, len(words)))
    }
    
    return metrics