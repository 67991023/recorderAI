import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from config import ML_CONFIG

# Check for ML libraries availability
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    ML_LIBS_AVAILABLE = True
except ImportError:
    ML_LIBS_AVAILABLE = False

def create_tfidf_vectors(texts: List[str]) -> Tuple[Optional[np.ndarray], Optional[TfidfVectorizer]]:
    """
    Create TF-IDF vectors from texts
    
    Args:
        texts: List of preprocessed texts
        
    Returns:
        Tuple[Optional[np.ndarray], Optional[TfidfVectorizer]]: TF-IDF matrix and vectorizer
    """
    if not ML_LIBS_AVAILABLE:
        print("❌ ML libraries not available")
        return None, None
    
    if not texts or len(texts) < 2:
        print("❌ Need at least 2 texts for TF-IDF")
        return None, None
    
    try:
        max_features = min(ML_CONFIG['max_tfidf_features'], len(' '.join(texts).split()))
        
        vectorizer = TfidfVectorizer(  # counts the words and considers the importance of words across all documents.
            max_features=max_features,
            min_df=ML_CONFIG['min_df'],
            max_df=ML_CONFIG['max_df'],
            ngram_range=ML_CONFIG['ngram_range'],
            strip_accents=None,
            lowercase=True,
            stop_words=None
        )
        
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        print(f"✅ TF-IDF vectors created: {tfidf_matrix.shape}")
        return tfidf_matrix, vectorizer
        
    except Exception as e:
        print(f"❌ TF-IDF creation error: {e}")
        return None, None

def perform_kmeans_clustering(tfidf_matrix: np.ndarray, n_clusters: int) -> Tuple[Optional[np.ndarray], Optional[KMeans]]:
    """
    Perform K-Means clustering on TF-IDF matrix
    
    Args:
        tfidf_matrix: TF-IDF feature matrix
        n_clusters: Number of clusters
        
    Returns:
        Tuple[Optional[np.ndarray], Optional[KMeans]]: Cluster labels and KMeans model
    """
    if not ML_LIBS_AVAILABLE:
        print("❌ ML libraries not available")
        return None, None
    
    if tfidf_matrix is None:
        print("❌ TF-IDF matrix is None")
        return None, None
    
    try:
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=ML_CONFIG['random_state'],
            n_init=ML_CONFIG['kmeans_n_init'],
            max_iter=ML_CONFIG['kmeans_max_iter']
        )
        
        clusters = kmeans.fit_predict(tfidf_matrix)
        
        print(f"✅ K-Means clustering completed: {n_clusters} clusters")
        return clusters, kmeans
        
    except Exception as e:
        print(f"❌ K-Means clustering error: {e}")
        return None, None

def calculate_silhouette_score_safe(tfidf_matrix: np.ndarray, clusters: np.ndarray) -> float:
    """
    Calculate silhouette score safely
    
    Args:
        tfidf_matrix: TF-IDF feature matrix
        clusters: Cluster labels
        
    Returns:
        float: Silhouette score
    """
    if not ML_LIBS_AVAILABLE:
        return 0.0
    
    try:
        if len(set(clusters)) > 1 and tfidf_matrix.shape[0] > len(set(clusters)):
            score = silhouette_score(tfidf_matrix, clusters)
            return score
    except Exception as e:
        print(f"⚠️ Silhouette score calculation error: {e}")
    
    return 0.0

def determine_optimal_clusters(tfidf_matrix: np.ndarray) -> int:
    """
    Determine optimal number of clusters
    
    Args:
        tfidf_matrix: TF-IDF feature matrix
        
    Returns:
        int: Optimal number of clusters
    """
    n_samples = tfidf_matrix.shape[0]
    
    if n_samples >= 8:
        return min(4, n_samples // 2)
    elif n_samples >= 6:
        return 3
    elif n_samples >= 4:
        return 2
    else:
        return 2

def extract_cluster_keywords(vectorizer: TfidfVectorizer, kmeans: KMeans, top_n: int = 3) -> Dict[int, List[str]]:
    """
    Extract keywords for each cluster
    
    Args:
        vectorizer: Fitted TF-IDF vectorizer
        kmeans: Fitted K-Means model
        top_n: Number of top keywords per cluster
        
    Returns:
        Dict[int, List[str]]: Cluster keywords
    """
    if not vectorizer or not kmeans:
        return {}
    
    try:
        feature_names = vectorizer.get_feature_names_out()
        cluster_centers = kmeans.cluster_centers_
        
        cluster_keywords = {}
        for i, center in enumerate(cluster_centers):
            top_indices = center.argsort()[-top_n:][::-1]
            keywords = [feature_names[idx] for idx in top_indices if center[idx] > 0]
            cluster_keywords[i] = keywords[:top_n]
        
        return cluster_keywords
        
    except Exception as e:
        print(f"⚠️ Keyword extraction error: {e}")
        return {}

def ml_text_classification(voice_records: List[Dict]) -> pd.DataFrame:
    """
    Perform complete ML text classification
    
    Args:
        voice_records: List of voice records
        
    Returns:
        pd.DataFrame: Results with ML classification
    """
    from Thai_textProcessing import preprocess_text_for_ml, fix_thai_word_count, classify_text_by_rules
    
    if not voice_records or len(voice_records) < 2:
        print("❌ Need at least 2 records for ML classification")
        return pd.DataFrame()
    
    print(f"🤖 Starting ML classification for {len(voice_records)} records...")
    
    try:
        # Fix word counts
        for record in voice_records:
            record['word_count'] = fix_thai_word_count(record['text'])
        
        # Prepare data
        texts = [record['text'] for record in voice_records]
        
        # Preprocess texts
        processed_texts = []
        for text in texts:
            tokens = preprocess_text_for_ml(text)
            processed_text = ' '.join(tokens[:30])  # Limit tokens
            processed_texts.append(processed_text)
        
        # Create DataFrame
        results_df = pd.DataFrame({
            'id': [r['id'] for r in voice_records],
            'text': texts,
            'processed_text': processed_texts,
            'timestamp': pd.to_datetime([r['timestamp'] for r in voice_records]),
            'word_count': [r['word_count'] for r in voice_records],
            'character_count': [r['character_count'] for r in voice_records]
        })
        
        # Rule-based classification
        results_df['rule_category'] = results_df['text'].apply(classify_text_by_rules)
        
        # ML classification
        tfidf_matrix, vectorizer = create_tfidf_vectors(processed_texts)
        
        if tfidf_matrix is not None:
            n_clusters = determine_optimal_clusters(tfidf_matrix)
            clusters, kmeans = perform_kmeans_clustering(tfidf_matrix, n_clusters)
            
            if clusters is not None:
                results_df['ml_cluster'] = clusters
                
                # Calculate metrics
                silhouette = calculate_silhouette_score_safe(tfidf_matrix, clusters)
                cluster_keywords = extract_cluster_keywords(vectorizer, kmeans)
                
                # Store metadata
                results_df.attrs['silhouette_score'] = silhouette
                results_df.attrs['cluster_keywords'] = cluster_keywords
                results_df.attrs['n_features'] = tfidf_matrix.shape[1]
                
                print(f"✅ ML Classification completed:")
                print(f"   • Clusters: {n_clusters}")
                print(f"   • Silhouette score: {silhouette:.3f}")
                print(f"   • Features: {tfidf_matrix.shape[1]}")
                
                for cluster_id, keywords in cluster_keywords.items():
                    print(f"   • Cluster {cluster_id}: {', '.join(keywords)}")
            else:
                results_df['ml_cluster'] = 0
        else:
            results_df['ml_cluster'] = 0
        
        return results_df
        
    except Exception as e:
        print(f"❌ ML classification error: {e}")
        return pd.DataFrame()

def analyze_cluster_characteristics(results_df: pd.DataFrame) -> Dict:
    """
    Analyze characteristics of each cluster
    
    Args:
        results_df: DataFrame with ML results
        
    Returns:
        Dict: Cluster characteristics
    """
    if results_df.empty or 'ml_cluster' not in results_df.columns:
        return {}
    
    cluster_analysis = {}
    
    for cluster_id in results_df['ml_cluster'].unique():
        cluster_data = results_df[results_df['ml_cluster'] == cluster_id]
        
        characteristics = {
            'count': len(cluster_data),
            'avg_word_count': cluster_data['word_count'].mean(),
            'avg_char_count': cluster_data['character_count'].mean(),
            'dominant_rule_category': cluster_data['rule_category'].mode().iloc[0] if not cluster_data['rule_category'].mode().empty else 'N/A',
            'word_count_std': cluster_data['word_count'].std(),
            'sample_texts': cluster_data['text'].head(3).tolist()
        }
        
        cluster_analysis[cluster_id] = characteristics
    
    return cluster_analysis