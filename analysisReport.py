"""
Analysis Report Functions (No Time Analysis)
===========================================
Author: User 67991023
Current Date and Time (UTC): 2025-08-28 07:12:49
"""

import os
from typing import Dict, List
import datetime
import pandas as pd
import numpy as np  # Added missing import
from config import APP_CONFIG, FILE_CONFIG

def generate_basic_summary(voice_records: List[Dict]) -> str:
    """
    Generate basic analysis summary (without time analysis)
    
    Args:
        voice_records: List of voice records
        
    Returns:
        str: Basic summary text
    """
    from text_processing import fix_thai_word_count  # Fixed import name
    from dataManagement import get_data_statistics   # Fixed import name
    
    if not voice_records:
        return "❌ No data available for analysis"
    
    print(f"📊 Generating basic summary for {len(voice_records)} records...")
    
    try:
        # Get statistics
        stats = get_data_statistics(voice_records)
        
        # Basic analysis
        dates = list(set([r.get('date', '') for r in voice_records if r.get('date')]))
        dates = [d for d in dates if d]  # Remove empty strings
        
        summary = f"""
📊 VOICE RECORDING ANALYSIS SUMMARY
{'=' * 50}
👤 User: {APP_CONFIG['user_login']}
📅 Analysis Date: {APP_CONFIG['current_datetime']}
🔖 Version: {APP_CONFIG['version']}

📈 DATASET OVERVIEW
• Total Recordings: {stats['total_records']:,}
• Recording Period: {len(dates)} day(s)
• Average per Day: {stats['total_records']/max(len(dates), 1):.1f} recordings

📝 WORD STATISTICS
• Total Words: {stats['word_statistics']['total_words']:,}
• Average Words per Recording: {stats['word_statistics']['mean_words']:.1f} ± {stats['word_statistics']['std_words']:.1f}
• Median Words per Recording: {stats['word_statistics']['median_words']:.1f}
• Word Range: {stats['word_statistics']['min_words']} - {stats['word_statistics']['max_words']} words
"""
        
        if len(dates) > 0:
            summary += f"• Words per Day: {stats['word_statistics']['total_words']/len(dates):.1f}\n"
        
        if 'character_statistics' in stats:
            char_stats = stats['character_statistics']
            summary += f"""
📊 CHARACTER STATISTICS  
• Total Characters: {char_stats['total_characters']:,}
• Average Characters per Recording: {char_stats['mean_characters']:.1f}
• Characters per Word Ratio: {char_stats['mean_characters']/stats['word_statistics']['mean_words']:.1f}
"""
        
        # Recording quality assessment
        word_stats = stats['word_statistics']
        short_recordings = sum(1 for r in voice_records if r.get('word_count', 0) <= 5)
        medium_recordings = sum(1 for r in voice_records if 6 <= r.get('word_count', 0) <= 20)
        long_recordings = sum(1 for r in voice_records if r.get('word_count', 0) > 20)
        
        summary += f"""
🎙️ RECORDING QUALITY
• Short Recordings (≤5 words): {short_recordings}
• Medium Recordings (6-20 words): {medium_recordings}
• Long Recordings (>20 words): {long_recordings}

📊 SUMMARY INSIGHTS
"""
        
        # Add insights
        mean_words = word_stats['mean_words']
        std_words = word_stats['std_words']
        
        if mean_words < 5:
            summary += "• Recordings tend to be short - consider longer sessions\n"
        elif mean_words > 50:
            summary += "• Recordings are quite detailed - good for comprehensive analysis\n"
        else:
            summary += "• Recording length is well-balanced\n"
        
        if std_words > mean_words:
            summary += "• High variability in recording length\n"
        else:
            summary += "• Consistent recording length pattern\n"
        
        if len(dates) == 1:
            summary += "• All recordings from single day - consider multi-day tracking\n"
        else:
            summary += f"• Good temporal spread across {len(dates)} days\n"
        
        summary += f"""
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
    """
    Generate ML analysis report (without time series)
    
    Args:
        results_df: DataFrame with ML results
        
    Returns:
        str: ML analysis report
    """
    if results_df.empty:
        return "❌ No ML analysis data available"
    
    print("🤖 Generating ML analysis report...")
    
    try:
        total_records = len(results_df)
        
        report = f"""
🤖 MACHINE LEARNING CLASSIFICATION REPORT
{'=' * 50}
👤 User: {APP_CONFIG['user_login']}
📅 Analysis Date: {APP_CONFIG['current_datetime']}
🔖 Version: {APP_CONFIG['version']}

📊 DATASET OVERVIEW
• Total Records Analyzed: {total_records:,}
• Analysis Type: ML Classification + Statistical Analysis
• Libraries Used: Scikit-learn, NumPy, Pandas, Matplotlib

🤖 MACHINE LEARNING CLASSIFICATION RESULTS
{'=' * 40}

📈 TF-IDF Analysis:
"""
        
        if hasattr(results_df, 'attrs') and 'n_features' in results_df.attrs:
            report += f"• TF-IDF Features: {results_df.attrs['n_features']}\n"
        
        # ML Clustering Results
        if 'ml_cluster' in results_df.columns:
            cluster_counts = results_df['ml_cluster'].value_counts().sort_index()
            report += f"""
📊 K-Means Clustering:
• Number of Clusters: {len(cluster_counts)}
"""
            
            if hasattr(results_df, 'attrs') and 'silhouette_score' in results_df.attrs:
                silhouette = results_df.attrs['silhouette_score']
                report += f"• Silhouette Score: {silhouette:.3f}\n"
                
                if silhouette > 0.5:
                    report += "• Clustering Quality: Excellent separation\n"
                elif silhouette > 0.3:
                    report += "• Clustering Quality: Good separation\n"
                else:
                    report += "• Clustering Quality: Moderate separation\n"
            
            # Cluster details
            for cluster_id, count in cluster_counts.items():
                percentage = (count / total_records) * 100
                cluster_data = results_df[results_df['ml_cluster'] == cluster_id]
                avg_words = cluster_data['word_count'].mean()
                
                report += f"  - Cluster {cluster_id}: {count} records ({percentage:.1f}%) - Avg: {avg_words:.1f} words\n"
                
                # Add keywords if available
                if hasattr(results_df, 'attrs') and 'cluster_keywords' in results_df.attrs:
                    keywords = results_df.attrs['cluster_keywords'].get(cluster_id, [])
                    if keywords:
                        report += f"    Keywords: {', '.join(keywords[:3])}\n"
        
        # Rule-based Classification
        if 'rule_category' in results_df.columns:
            category_counts = results_df['rule_category'].value_counts()
            report += f"""
📂 Rule-based Classification:
• Number of Categories: {len(category_counts)}
"""
            
            for category, count in category_counts.items():
                percentage = (count / total_records) * 100
                avg_words = results_df[results_df['rule_category'] == category]['word_count'].mean()
                report += f"  - {category}: {count} records ({percentage:.1f}%) - Avg: {avg_words:.1f} words\n"
        
        # Statistical Analysis
        word_counts = results_df['word_count'].values
        char_counts = results_df['character_count'].values
        
        report += f"""
📊 STATISTICAL ANALYSIS
{'=' * 30}
• Word Count Statistics:
  - Mean: {word_counts.mean():.1f} ± {word_counts.std():.1f}
  - Median: {np.median(word_counts):.1f}
  - Range: {word_counts.min()} - {word_counts.max()}

• Character Count Statistics:
  - Mean: {char_counts.mean():.1f} ± {char_counts.std():.1f}
  - Word-Character Correlation: {np.corrcoef(word_counts, char_counts)[0,1]:.3f}
"""
        
        # Insights and Recommendations
        report += f"""
💡 INSIGHTS AND RECOMMENDATIONS
{'=' * 35}
"""
        
        # ML Insights
        if 'ml_cluster' in results_df.columns and len(results_df['ml_cluster'].unique()) > 1:
            report += "• ML clustering successfully identified distinct patterns in your recordings\n"
            
            if hasattr(results_df, 'attrs') and 'silhouette_score' in results_df.attrs:
                silhouette = results_df.attrs['silhouette_score']
                if silhouette > 0.3:
                    report += "• High-quality clustering suggests clear thematic differences\n"
                else:
                    report += "• Moderate clustering suggests some overlap between topics\n"
        else:
            report += "• Consider more diverse recording topics for better ML analysis\n"
        
        # Data Quality Insights
        avg_words = word_counts.mean()
        if avg_words < 10:
            report += "• Consider longer recordings for better analysis depth\n"
        elif avg_words > 100:
            report += "• Very detailed recordings - excellent for comprehensive analysis\n"
        
        report += f"""
🔬 TECHNICAL METHODOLOGY
{'=' * 25}
• Text Processing: TF-IDF Vectorization with n-grams
• Clustering: K-Means with optimized cluster selection
• Statistical Analysis: NumPy and Pandas operations
• Visualization: Matplotlib with enhanced charts

📊 DATA QUALITY ASSESSMENT
{'=' * 27}
• Data Completeness: {(1 - results_df.isnull().sum().sum() / (len(results_df) * len(results_df.columns))) * 100:.1f}%
• Feature Richness: {len(results_df.columns)} attributes per record
• Analysis Coverage: {len(results_df)} records processed

🎯 CONCLUSIONS
{'=' * 15}
• ML Classification: {'Successful' if len(results_df['ml_cluster'].unique()) > 1 else 'Limited by data size'}
• Text Analysis: {'High-quality patterns identified' if avg_words > 15 else 'Basic patterns detected'}
• Overall Quality: {'Excellent dataset for analysis' if avg_words > 15 and len(results_df) > 5 else 'Good foundation for analysis'}

{'=' * 50}
Generated: {APP_CONFIG['current_datetime']}
Analysis completed using ML classification and statistical methods.
User: {APP_CONFIG['user_login']}
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error generating ML analysis report: {e}"

def save_analysis_report(report_content: str, report_type: str = "basic") -> str:
    """
    Save analysis report to file
    
    Args:
        report_content: Report content to save
        report_type: Type of report (basic, ml, comprehensive)
        
    Returns:
        str: Path to saved report
    """
    timestamp = APP_CONFIG['current_datetime'].replace(':', '-').replace(' ', '_')
    filename = f"{report_type}_analysis_report_{timestamp}.txt"
    output_path = os.path.join(FILE_CONFIG['output_dir'], filename)
    
    try:
        os.makedirs(FILE_CONFIG['output_dir'], exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 Analysis report saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error saving analysis report: {e}")
        return ""

def create_project_summary(voice_records: List[Dict], results_df: pd.DataFrame = None) -> str:
    """
    Create project summary for presentation (without time analysis)
    
    Args:
        voice_records: List of voice records
        results_df: ML analysis results
        
    Returns:
        str: Project summary
    """
    print("📊 Creating project presentation summary...")
    
    from dataManagement import get_data_statistics  # Fixed import name
    summary_stats = get_data_statistics(voice_records)
    
    presentation = f"""
🎯 THAI VOICE RECORDER WITH ML ANALYTICS
{'=' * 55}
Project Presentation Summary
User: {APP_CONFIG['user_login']} | Date: {APP_CONFIG['current_datetime']}

📋 ABSTRACT
This project implements a Thai voice recording system with machine learning 
analytics capabilities, featuring TF-IDF text classification, K-Means clustering, 
and comprehensive statistical visualization tools.

🎯 OBJECTIVES
• Develop efficient Thai voice recording and transcription system
• Implement ML text classification using TF-IDF and K-Means
• Create comprehensive data visualization and reporting tools
• Provide statistical analysis of voice recording patterns

📚 LIBRARIES/MODULES USED
✅ NumPy: Advanced statistical calculations and array operations
✅ Pandas: Data manipulation, aggregation, and DataFrame operations  
✅ Matplotlib: Data visualization, charts, and statistical plots
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
4. 📊 Visualization → Matplotlib charts + statistical reports
5. 📋 Analysis → Comprehensive reporting system

📈 RESULTS/OUTPUT
"""
    
    # Add results based on available data
    if summary_stats['word_analysis']:
        word_stats = summary_stats['word_analysis']
        presentation += f"""
📝 Word Analysis Results:
• Total Words Processed: {word_stats['total_words']:,}
• Average Words per Recording: {word_stats['mean_words']:.1f}
• Word Count Range: {word_stats['min_words']} - {word_stats['max_words']}
"""
    
    if results_df is not None and not results_df.empty:
        ml_clusters = len(results_df['ml_cluster'].unique()) if 'ml_cluster' in results_df.columns else 0
        rule_categories = len(results_df['rule_category'].unique()) if 'rule_category' in results_df.columns else 0
        
        presentation += f"""
🤖 Machine Learning Results:
• ML Clusters Identified: {ml_clusters}
• Rule-based Categories: {rule_categories}
"""
        
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
• Dataset Size: {summary_stats['overview']['total_records']} recordings
• Quality Distribution:
  - Short (≤5 words): {summary_stats['quality_metrics']['short_recordings']}
  - Medium (6-20 words): {summary_stats['quality_metrics']['medium_recordings']}  
  - Long (>20 words): {summary_stats['quality_metrics']['long_recordings']}

🏆 CONCLUSION
This project successfully demonstrates the integration of voice recording 
technology with machine learning analytics, providing comprehensive insights 
through text classification and statistical analysis.

{'=' * 55}
Generated: {APP_CONFIG['current_datetime']}
Project completed by User: {APP_CONFIG['user_login']}
"""
    
    return presentation