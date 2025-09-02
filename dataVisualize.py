"""
Data Visualization Functions
Author: User 67991023, Current Date: 2025-09-02 06:47:37
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import os
from config import VIS_CONFIG, APP_CONFIG

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

def configure_matplotlib():
    """Configure matplotlib settings"""
    plt.rcParams['figure.figsize'] = VIS_CONFIG['figure_size']
    plt.rcParams['font.size'] = VIS_CONFIG['font_size']
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 10
    plt.style.use('default')
    
    # Font configuration
    try:
        import matplotlib.font_manager as fm
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        selected_font = None
        for font in VIS_CONFIG['thai_fonts']:
            if font in available_fonts:
                selected_font = font
                break
        
        if selected_font:
            plt.rcParams['font.family'] = [selected_font]
        else:
            plt.rcParams['font.family'] = ['sans-serif']
            
    except Exception:
        plt.rcParams['font.family'] = ['sans-serif']

def create_word_count_distribution_chart(voice_records: List[Dict], output_dir: str = "analysis_outputs") -> str:
    """Create word count distribution visualization"""
    from Thai_textProcessing import fix_thai_word_count
    
    if not voice_records:
        return ""
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Fix word counts
        for record in voice_records:
            if 'word_count' not in record or record['word_count'] <= 0:
                record['word_count'] = fix_thai_word_count(record['text'])
        
        word_counts = [record['word_count'] for record in voice_records]
        
        # Create the chart
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        # Enhanced histogram
        n_bins = min(15, len(word_counts))
        counts, bins, patches = ax.hist(
            word_counts, 
            bins=n_bins,
            alpha=0.7, 
            color=VIS_CONFIG['colors']['primary'], 
            edgecolor='navy',
            linewidth=1.5
        )
        
        # Calculate and display statistics
        mean_words = np.mean(word_counts)
        median_words = np.median(word_counts)
        std_words = np.std(word_counts)
        
        # Add statistical lines
        ax.axvline(mean_words, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_words:.1f}')
        ax.axvline(median_words, color='green', linestyle='--', linewidth=2, label=f'Median: {median_words:.1f}')
        
        # Formatting
        ax.set_title(f'Word Count Distribution\nUser: {APP_CONFIG["user_login"]} | {APP_CONFIG["current_datetime"]}', 
                    fontsize=14, pad=20)
        ax.set_xlabel('Number of Words per Recording', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Add statistics text box
        stats_text = f"""Statistics Summary:
Total Records: {len(word_counts)}
Mean: {mean_words:.1f} ± {std_words:.1f}
Median: {median_words:.1f}
Min: {min(word_counts)}
Max: {max(word_counts)}
Range: {max(word_counts) - min(word_counts)}"""
        
        ax.text(0.65, 0.95, stats_text, transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
               fontsize=10, verticalalignment='top')
        
        plt.tight_layout()
        
        # Save chart
        output_file = f'{output_dir}/word_count_distribution.png'
        plt.savefig(output_file, dpi=VIS_CONFIG['dpi'], bbox_inches='tight', facecolor='white')
        
        print(f"✅ Word count distribution saved: {output_file}")
        plt.show()
        
        return output_file
        
    except Exception as e:
        print(f"❌ Word count distribution error: {e}")
        return ""

def create_ml_classification_charts(results_df: pd.DataFrame, output_dir: str = "analysis_outputs") -> str:
    """Create ML classification visualization charts"""
    if results_df.empty:
        return ""
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Cluster Distribution
        if 'ml_cluster' in results_df.columns:
            cluster_counts = results_df['ml_cluster'].value_counts().sort_index()
            colors = plt.cm.Set3(np.linspace(0, 1, len(cluster_counts)))
            ax1.pie(cluster_counts.values, labels=[f'Cluster {i}' for i in cluster_counts.index],
                   autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title('ML Cluster Distribution', fontsize=14)
        
        # 2. Word Count by Cluster
        if 'ml_cluster' in results_df.columns and 'word_count' in results_df.columns:
            cluster_word_counts = [results_df[results_df['ml_cluster'] == cluster]['word_count'].values 
                                 for cluster in sorted(results_df['ml_cluster'].unique())]
            ax2.boxplot(cluster_word_counts, labels=[f'C{i}' for i in range(len(cluster_word_counts))])
            ax2.set_title('Word Count by Cluster', fontsize=14)
            ax2.set_xlabel('Cluster')
            ax2.set_ylabel('Word Count')
        
        # 3. Rule Categories
        if 'rule_category' in results_df.columns:
            category_counts = results_df['rule_category'].value_counts()
            colors = plt.cm.Pastel1(np.linspace(0, 1, len(category_counts)))
            ax3.pie(category_counts.values, 
                   labels=[cat[:10] + '...' if len(cat) > 10 else cat for cat in category_counts.index],
                   autopct='%1.1f%%', colors=colors, startangle=90)
            ax3.set_title('Text Categories', fontsize=12)
        
        # 4. Character vs Word Count
        if 'word_count' in results_df.columns and 'character_count' in results_df.columns:
            scatter = ax4.scatter(results_df['word_count'], results_df['character_count'], 
                                 alpha=0.7, color='orange', s=60, edgecolor='darkorange')
            ax4.set_title('Words vs Characters', fontsize=12)
            ax4.set_xlabel('Word Count')
            ax4.set_ylabel('Character Count')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        output_file = f'{output_dir}/ml_classification_charts.png'
        plt.savefig(output_file, dpi=VIS_CONFIG['dpi'], bbox_inches='tight', facecolor='white')
        
        print(f"✅ ML classification charts saved: {output_file}")
        plt.show()
        
        return output_file
        
    except Exception as e:
        print(f"❌ ML classification charts error: {e}")
        return ""

def create_comprehensive_dashboard(results_df: pd.DataFrame, output_dir: str = "analysis_outputs") -> str:
    """Create comprehensive analysis dashboard"""
    if results_df.empty:
        return ""
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        fig = plt.figure(figsize=(18, 12))
        
        # 1. Word Count Histogram
        ax1 = plt.subplot(2, 3, 1)
        word_counts = results_df['word_count']
        ax1.hist(word_counts, bins=15, alpha=0.7, color='skyblue', edgecolor='navy')
        ax1.set_title('Word Count Distribution', fontsize=12)
        ax1.set_xlabel('Word Count')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # 2. ML Clusters
        ax2 = plt.subplot(2, 3, 2)
        if 'ml_cluster' in results_df.columns:
            cluster_counts = results_df['ml_cluster'].value_counts().sort_index()
            colors = plt.cm.Set3(np.linspace(0, 1, len(cluster_counts)))
            ax2.pie(cluster_counts.values, labels=[f'Cluster {i}' for i in cluster_counts.index],
                   autopct='%1.1f%%', colors=colors, startangle=90)
            ax2.set_title('ML Clusters', fontsize=12)
        
        # 3. Categories
        ax3 = plt.subplot(2, 3, 3)
        if 'rule_category' in results_df.columns:
            category_counts = results_df['rule_category'].value_counts()
            colors = plt.cm.Pastel1(np.linspace(0, 1, len(category_counts)))
            ax3.pie(category_counts.values, 
                   labels=[cat[:10] + '...' if len(cat) > 10 else cat for cat in category_counts.index],
                   autopct='%1.1f%%', colors=colors, startangle=90)
            ax3.set_title('Text Categories', fontsize=12)
        
        # 4. Character vs Word Count
        ax4 = plt.subplot(2, 3, 4)
        scatter = ax4.scatter(results_df['word_count'], results_df['character_count'], 
                             alpha=0.7, color='orange', s=60, edgecolor='darkorange')
        ax4.set_title('Words vs Characters', fontsize=12)
        ax4.set_xlabel('Word Count')
        ax4.set_ylabel('Character Count')
        ax4.grid(True, alpha=0.3)
        
        # 5. Cluster Word Counts
        ax5 = plt.subplot(2, 3, 5)
        if 'ml_cluster' in results_df.columns:
            cluster_word_counts = [results_df[results_df['ml_cluster'] == cluster]['word_count'].values 
                                 for cluster in sorted(results_df['ml_cluster'].unique())]
            ax5.boxplot(cluster_word_counts, labels=[f'C{i}' for i in range(len(cluster_word_counts))])
            ax5.set_title('Word Count by Cluster', fontsize=12)
            ax5.set_xlabel('Cluster')
            ax5.set_ylabel('Word Count')
            ax5.grid(True, alpha=0.3)
        
        # 6. Statistics Panel
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        # Calculate stats
        total_records = len(results_df)
        avg_words = results_df['word_count'].mean()
        std_words = results_df['word_count'].std()
        
        stats_text = f"""📊 Analysis Dashboard

📈 Overview:
• Total Records: {total_records}
• Avg Words/Record: {avg_words:.1f} ± {std_words:.1f}

🤖 ML Results:
• Clusters: {len(results_df['ml_cluster'].unique()) if 'ml_cluster' in results_df.columns else 'N/A'}
• Categories: {len(results_df['rule_category'].unique()) if 'rule_category' in results_df.columns else 'N/A'}

📊 Data Quality:
• Min Words: {results_df['word_count'].min()}
• Max Words: {results_df['word_count'].max()}
• Range: {results_df['word_count'].max() - results_df['word_count'].min()}

📅 Analysis Info:
• User: {APP_CONFIG['user_login']}
• Time: {APP_CONFIG['current_datetime']}
• Version: {APP_CONFIG['version']}
• Features: ML + Visualization
"""
        
        ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        plt.tight_layout()
        
        # Save dashboard
        output_file = f'{output_dir}/comprehensive_dashboard.png'
        plt.savefig(output_file, dpi=VIS_CONFIG['dpi'], bbox_inches='tight', facecolor='white')
        
        print(f"✅ Comprehensive dashboard saved: {output_file}")
        plt.show()
        
        return output_file
        
    except Exception as e:
        print(f"❌ Dashboard creation error: {e}")
        return ""