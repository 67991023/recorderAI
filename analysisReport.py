"""
Analysis Report Functions
Author: User 67991023, Current Date: 2025-09-02 06:47:37
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
    
    try:
        # Get statistics
        stats = get_data_statistics(voice_records)
        
        # Basic analysis
        dates = list(set([r.get('date', '') for r in voice_records if r.get('date')]))
        dates = [d for d in dates if d]
        
        summary = f"""
📊 VOICE RECORDING ANALYSIS SUMMARY
{'=' * 50}
👤 User: {APP_CONFIG['user_login']}
📅 Analysis Date: {APP_CONFIG['current_datetime']}
🔖 Version: {APP_CONFIG['version']}

📈 DATASET OVERVIEW
• Total Recordings: {stats['total_records']:,}
• Recording Period: {len(dates)} day(s)

📊 WORD ANALYSIS
• Total Words: {stats['word_statistics']['total_words']:,}
• Average Words/Recording: {stats['word_statistics']['mean_words']:.1f}
• Range: {stats['word_statistics']['min_words']} - {stats['word_statistics']['max_words']} words

📋 QUALITY METRICS
• Short Recordings (≤5 words): {sum(1 for r in voice_records if r.get('word_count', 0) <= 5)}
• Medium Recordings (6-20 words): {sum(1 for r in voice_records if 6 <= r.get('word_count', 0) <= 20)}
• Long Recordings (>20 words): {sum(1 for r in voice_records if r.get('word_count', 0) > 20)}

🔧 TECHNICAL INFO
• Analysis Method: Statistical Computing + ML Classification
• Word Counting: {'Thai Tokenization (pythainlp)' if 'pythainlp' in str(type(fix_thai_word_count)) else 'Estimation Method'}
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
    """Generate comprehensive ML analysis report"""
    if results_df.empty:
        return "❌ No ML results available for analysis"
    
    try:
        # Extract metadata
        silhouette_score = results_df.attrs.get('silhouette_score', 0.0)
        cluster_keywords = results_df.attrs.get('cluster_keywords', {})
        n_features = results_df.attrs.get('n_features', 0)
        
        # Calculate statistics
        total_records = len(results_df)
        n_clusters = len(results_df['ml_cluster'].unique()) if 'ml_cluster' in results_df.columns else 0
        n_categories = len(results_df['rule_category'].unique()) if 'rule_category' in results_df.columns else 0
        
        # Word statistics
        word_mean = results_df['word_count'].mean()
        word_std = results_df['word_count'].std()
        
        # Cluster analysis
        cluster_info = ""
        if 'ml_cluster' in results_df.columns:
            for cluster_id in sorted(results_df['ml_cluster'].unique()):
                cluster_data = results_df[results_df['ml_cluster'] == cluster_id]
                cluster_size = len(cluster_data)
                cluster_mean_words = cluster_data['word_count'].mean()
                
                keywords = cluster_keywords.get(cluster_id, [])
                keywords_str = ', '.join(keywords[:3]) if keywords else "N/A"
                
                cluster_info += f"""
  🏷️ Cluster {cluster_id}: {cluster_size} records ({cluster_size/total_records*100:.1f}%)
     • Avg Words: {cluster_mean_words:.1f}
     • Keywords: {keywords_str}"""
        
        # Category analysis
        category_info = ""
        if 'rule_category' in results_df.columns:
            category_counts = results_df['rule_category'].value_counts()
            for category, count in category_counts.head(5).items():
                category_info += f"""
  📂 {category}: {count} records ({count/total_records*100:.1f}%)"""
        
        report = f"""
🤖 MACHINE LEARNING ANALYSIS REPORT
{'=' * 55}

📊 DATASET ANALYSIS
• Total Records Processed: {total_records:,}
• ML Features Generated: {n_features}
• Average Words per Record: {word_mean:.1f} ± {word_std:.1f}

🧠 CLUSTERING RESULTS
• Number of Clusters: {n_clusters}
• Clustering Quality (Silhouette): {silhouette_score:.3f}
• Cluster Performance: {'Good' if silhouette_score > 0.3 else 'Moderate' if silhouette_score > 0.1 else 'Poor'}
{cluster_info}

📂 RULE-BASED CLASSIFICATION
• Number of Categories: {n_categories}
{category_info}

📈 INSIGHTS & RECOMMENDATIONS
• Data Quality: {'Excellent' if word_mean > 10 else 'Good' if word_mean > 5 else 'Needs Improvement'}
• Cluster Separation: {'Well-separated' if silhouette_score > 0.3 else 'Moderately separated' if silhouette_score > 0.1 else 'Overlapping'}
• Dataset Size: {'Adequate for ML' if total_records >= 10 else 'Small - consider collecting more data'}

{'=' * 55}
Generated: {APP_CONFIG['current_datetime']}
User: {APP_CONFIG['user_login']}
ML Analysis Version: {APP_CONFIG['version']}
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error generating ML report: {e}"

def save_analysis_report(report_content: str, report_type: str = "basic") -> str:
    """Save analysis report to file"""
    os.makedirs(FILE_CONFIG['output_dir'], exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{report_type}_analysis_report_{timestamp}.txt"
    output_path = os.path.join(FILE_CONFIG['output_dir'], filename)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 Report saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error saving report: {e}")
        return ""

def create_project_summary(voice_records: List[Dict], results_df: pd.DataFrame = None) -> str:
    """Create comprehensive project summary"""
    try:
        # Get basic statistics
        from dataManagement import get_data_statistics
        summary_stats = get_data_statistics(voice_records) if voice_records else {}
        
        presentation = f"""
🎯 THAI VOICE RECORDER PROJECT SUMMARY
{'=' * 55}

📋 PROJECT OVERVIEW
This project implements an advanced Thai voice recording system with integrated 
machine learning analytics for text classification and data visualization.

🎯 OBJECTIVES ACHIEVED
✅ Real-time Thai voice recording and transcription
✅ Automated text processing and word counting
✅ Machine learning classification (TF-IDF + K-Means)
✅ Comprehensive data visualization and reporting tools
✅ Statistical analysis of voice recording patterns

📚 LIBRARIES/MODULES USED
✅ NumPy: Advanced statistical calculations and array operations
✅ Pandas: Data manipulation, aggregation, and DataFrame operations  
✅ Matplotlib: Data visualization, charts, and statistical plots
✅ Scikit-learn: TF-IDF vectorization, K-Means clustering, ML metrics

📊 NATURE OF DATA
• Voice Records: {summary_stats.get('total_records', 0)} Thai language recordings
• Text Data: Transcribed speech with word/character counts
• Metadata: User info, session data, categories, ML features
• Statistical Data: Word distributions, cluster assignments

⚙️ METHODOLOGY
1. 🎙️ Voice Recording → Speech Recognition (Google API)
2. 📝 Text Processing → Thai tokenization (pythainlp)
3. 🤖 ML Classification → TF-IDF → K-Means Clustering
4. 📊 Visualization → Matplotlib charts + statistical reports
5. 📋 Analysis → Comprehensive reporting system

📈 RESULTS/OUTPUT"""
        
        # Add results based on available data
        if summary_stats.get('word_statistics'):
            word_stats = summary_stats['word_statistics']
            presentation += f"""

📝 Word Analysis Results:
• Total Words Processed: {word_stats['total_words']:,}
• Average Words per Recording: {word_stats['mean_words']:.1f}
• Word Count Range: {word_stats['min_words']} - {word_stats['max_words']}"""
        
        if results_df is not None and not results_df.empty:
            ml_clusters = len(results_df['ml_cluster'].unique()) if 'ml_cluster' in results_df.columns else 0
            rule_categories = len(results_df['rule_category'].unique()) if 'rule_category' in results_df.columns else 0
            
            presentation += f"""

🤖 Machine Learning Results:
• ML Clusters Identified: {ml_clusters}
• Rule-based Categories: {rule_categories}"""
            
            if hasattr(results_df, 'attrs') and 'silhouette_score' in results_df.attrs:
                silhouette = results_df.attrs['silhouette_score']
                presentation += f"• Clustering Quality (Silhouette): {silhouette:.3f}\n"
        
        presentation += f"""

💻 IMPLEMENTATION
• Programming Language: Python 3.x
• Architecture: Modular design with separated functions
• Voice Processing: SpeechRecognition + pyttsx3
• Data Storage: JSON with backup system
• Analytics Pipeline: Integrated ML and statistical analysis
• User Interface: Interactive command-line interface

📚 REFERENCES
• Scikit-learn Documentation: Machine Learning algorithms
• Matplotlib Documentation: Data visualization techniques
• Pandas Documentation: Data manipulation and analysis
• NumPy Documentation: Numerical computing foundations
• pythainlp Documentation: Thai natural language processing

🎯 PROJECT ACHIEVEMENTS
✅ Successfully implemented Thai voice recording system
✅ Developed ML text classification with {f"{len(results_df['ml_cluster'].unique())} clusters" if results_df is not None and not results_df.empty else "clustering capabilities"}
✅ Created comprehensive data visualization tools
✅ Generated automated analysis reports
✅ Achieved modular, maintainable code architecture

📊 STATISTICAL SUMMARY
• Dataset Size: {summary_stats.get('total_records', 0)} recordings
• Quality Distribution:
  - Short (≤5 words): {sum(1 for r in voice_records if r.get('word_count', 0) <= 5) if voice_records else 0}
  - Medium (6-20 words): {sum(1 for r in voice_records if 6 <= r.get('word_count', 0) <= 20) if voice_records else 0}
  - Long (>20 words): {sum(1 for r in voice_records if r.get('word_count', 0) > 20) if voice_records else 0}

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
        return f"❌ Error generating project summary: {e}"