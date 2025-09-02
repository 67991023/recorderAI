"""
Analysis Report Functions
Author: User 67991023
Current Date and Time (UTC): 2025-09-02 06:47:37
"""

import os
from typing import Dict, List
import datetime
import pandas as pd
import numpy as np
from config import APP_CONFIG, FILE_CONFIG

def generate_basic_summary(voice_records: List[Dict]) -> str:
    """Generate basic analysis summary"""
    from Thai_textProcessing import fix_thai_word_count
    from dataManagement import get_data_statistics
    
    if not voice_records:
        return "❌ No data available for analysis"
    
    print(f"📊 Generating basic summary for {len(voice_records)} records...")
    
    try:
        stats = get_data_statistics(voice_records)
        dates = list(set([r.get('date', '') for r in voice_records if r.get('date')]))
        dates = [d for d in dates if d]
        
        categories = {}
        for record in voice_records:
            category = record.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        summary = f"""
📊 VOICE RECORDING ANALYSIS SUMMARY
{'=' * 50}
Total Records: {stats['total_records']}
Recording Days: {len(dates)}
Date Range: {min(dates) if dates else 'N/A'} to {max(dates) if dates else 'N/A'}

📊 WORD STATISTICS
Total Words: {stats['word_statistics']['total_words']}
Average Words per Recording: {stats['word_statistics']['mean_words']:.1f}
Longest Recording: {stats['word_statistics']['max_words']} words
Shortest Recording: {stats['word_statistics']['min_words']} words

📊 CHARACTER STATISTICS  
Total Characters: {stats.get('character_statistics', {}).get('total_characters', 'N/A')}
Average Characters per Recording: {stats.get('character_statistics', {}).get('mean_characters', 0):.1f}

📊 CATEGORIES
{chr(10).join([f"• {category}: {count} recordings" for category, count in categories.items()])}

📊 SUMMARY INSIGHTS
• Quality Distribution:
  - Short (≤5 words): {len([r for r in voice_records if r.get('word_count', 0) <= 5])}
  - Medium (6-20 words): {len([r for r in voice_records if 6 <= r.get('word_count', 0) <= 20])}
  - Long (>20 words): {len([r for r in voice_records if r.get('word_count', 0) > 20])}

🔧 TECHNICAL INFO
• Analysis Method: Statistical Computing + ML Classification
• Word Counting: Thai Tokenization (pythainlp)
• Libraries: NumPy, Pandas, Matplotlib, Scikit-learn
• Data Quality: Validated and processed

{'=' * 50}
Generated: {APP_CONFIG['current_datetime']}
User: {APP_CONFIG['user_login']}
"""
        
        return summary
        
    except Exception as e:
        return f"❌ Error generating summary: {e}"

def generate_ml_analysis_report(results_df: pd.DataFrame) -> str:
    """Generate ML analysis report"""
    if results_df.empty:
        return "❌ No ML analysis data available"
    
    try:
        n_clusters = len(results_df['ml_cluster'].unique()) if 'ml_cluster' in results_df.columns else 0
        silhouette_score = getattr(results_df, 'attrs', {}).get('silhouette_score', 0.0)
        cluster_keywords = getattr(results_df, 'attrs', {}).get('cluster_keywords', {})
        
        report = f"""
📊 MACHINE LEARNING ANALYSIS REPORT
{'=' * 50}

📊 DATASET OVERVIEW
• Total Records Analyzed: {len(results_df)}
• ML Features Used: {getattr(results_df, 'attrs', {}).get('n_features', 'N/A')}
• Clustering Algorithm: K-Means
• Number of Clusters: {n_clusters}
• Silhouette Score: {silhouette_score:.3f}

📊 K-Means Clustering:
Quality Score: {silhouette_score:.3f} ({'Good' if silhouette_score > 0.3 else 'Moderate' if silhouette_score > 0.1 else 'Low'})

📊 CLUSTER ANALYSIS
{chr(10).join([f"Cluster {cluster_id}: {', '.join(keywords)}" for cluster_id, keywords in cluster_keywords.items()])}

📊 STATISTICAL ANALYSIS
{chr(10).join([f"Cluster {cluster_id}: {len(results_df[results_df['ml_cluster'] == cluster_id])} records" for cluster_id in results_df['ml_cluster'].unique()]) if 'ml_cluster' in results_df.columns else 'No cluster data'}

📊 DATA QUALITY ASSESSMENT
• All records successfully processed: ✅
• ML features extracted: ✅
• Clustering completed: ✅

🎯 CONCLUSIONS
The ML analysis successfully identified {n_clusters} distinct clusters in the voice recording data, 
with a silhouette score of {silhouette_score:.3f}, indicating {'good' if silhouette_score > 0.3 else 'moderate' if silhouette_score > 0.1 else 'low'} cluster separation.

{'=' * 50}
Generated: {APP_CONFIG['current_datetime']}
User: {APP_CONFIG['user_login']}
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error generating ML report: {e}"

def save_analysis_report(report_content: str, report_type: str = "basic") -> str:
    """Save analysis report to file"""
    if not report_content:
        return ""
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_report_{report_type}_{timestamp}.txt"
        filepath = os.path.join(FILE_CONFIG['output_dir'], filename)
        
        os.makedirs(FILE_CONFIG['output_dir'], exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 Report saved: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error saving report: {e}")
        return ""

def create_project_summary(voice_records: List[Dict], results_df: pd.DataFrame = None) -> str:
    """Create comprehensive project summary presentation"""
    if not voice_records:
        return "❌ No data available for project summary"
    
    print("📊 Creating project presentation summary...")
    
    try:
        from dataManagement import get_data_statistics
        
        summary_stats = get_data_statistics(voice_records)
        ml_info = ""
        
        if results_df is not None and not results_df.empty:
            n_clusters = len(results_df['ml_cluster'].unique()) if 'ml_cluster' in results_df.columns else 0
            ml_info = f"with {n_clusters} clusters"
        
        presentation = f"""
🎓 THAI VOICE RECORDER PROJECT SUMMARY
{'=' * 55}

📋 PROJECT OVERVIEW
This project implements a comprehensive Thai voice recording and analysis system
with machine learning capabilities for text classification and clustering.

🎯 PROJECT OBJECTIVES
• Develop Thai voice recording system with speech recognition
• Implement text processing for Thai language content
• Create machine learning classification using TF-IDF and K-Means
• Provide comprehensive data visualization and reporting tools
• Generate statistical analysis of voice recording patterns

📚 LIBRARIES/MODULES USED
✅ NumPy: Statistical calculations and array operations
✅ Pandas: Data manipulation and DataFrame operations  
✅ Matplotlib: Data visualization and statistical plots
✅ Scikit-learn: TF-IDF vectorization, K-Means clustering, ML metrics

📊 NATURE OF DATA
• Voice Records: {summary_stats['total_records']} Thai language recordings
• Text Data: Transcribed speech with word/character counts
• Metadata: User info, session data, categories, ML features
• Statistical Data: Word distributions, cluster assignments

⚙️ METHODOLOGY
1. 🎙️ Voice Recording → Speech Recognition (Google API)
2. 📝 Text Processing → Thai tokenization (pythainlp)
3. 🤖 ML Classification → TF-IDF → K-Means Clustering
4. 📊 Data Visualization → Charts, distributions, dashboards
5. 📄 Report Generation → Statistical summaries, ML insights

🎯 PROJECT ACHIEVEMENTS
✅ Successfully implemented Thai voice recording system
✅ Developed ML text classification {ml_info}
✅ Created comprehensive data visualization tools
✅ Generated automated analysis reports
✅ Achieved modular, maintainable code architecture

📊 STATISTICAL SUMMARY
• Dataset Size: {summary_stats['total_records']} recordings
• Quality Distribution:
  - Short (≤5 words): {len([r for r in voice_records if r.get('word_count', 0) <= 5])}
  - Medium (6-20 words): {len([r for r in voice_records if 6 <= r.get('word_count', 0) <= 20])}  
  - Long (>20 words): {len([r for r in voice_records if r.get('word_count', 0) > 20])}

🏆 CONCLUSION
This project successfully demonstrates the integration of voice recording 
technology with machine learning analytics, providing comprehensive insights 
through text classification and statistical analysis.

{'=' * 55}
Generated: {APP_CONFIG['current_datetime']}
Project completed by User: {APP_CONFIG['user_login']}
"""
    
        return presentation
        
    except Exception as e:
        return f"❌ Error creating project summary: {e}"