"""
Data Visualization Functions
Author: User 67991023
Current Date and Time (UTC): 2025-09-02 06:47:37
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
            print(f"✅ Using font: {selected_font}")
        else:
            plt.rcParams['font.family'] = ['sans-serif']
            print("⚠️ Using default font")
            
    except Exception as e:
        print(f"⚠️ Font configuration warning: {e}")

def create_word_count_distribution_chart(voice_records: List[Dict], output_dir: str = "analysis_outputs") -> str:
    """Create word count distribution chart"""
    from Thai_textProcessing import fix_thai_word_count
    
    if not voice_records:
        print("❌ No voice records for visualization")
        return ""
    
    configure_matplotlib()
    
    try:
        for record in voice_records:
            if 'word_count' not in record or record['word_count'] <= 0:
                record['word_count'] = fix_thai_word_count(record['text'])
        
        word_counts = [record['word_count'] for record in voice_records]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Histogram
        ax1.hist(word_counts, bins=min(20, len(set(word_counts))), 
                color=VIS_CONFIG['colors']['primary'], alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Word Count')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Distribution of Word Counts')
        ax1.grid(True, alpha=0.3)
        
        stats_text = f"""Statistics:
Total Records: {len(voice_records)}
Mean: {np.mean(word_counts):.1f}
Median: {np.median(word_counts):.1f}
Std: {np.std(word_counts):.1f}
Min: {min(word_counts)}
Max: {max(word_counts)}"""
        
        ax1.text(0.98, 0.98, stats_text, transform=ax1.transAxes, 
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Box plot
        ax2.boxplot(word_counts, labels=['Word Counts'])
        ax2.set_ylabel('Word Count')
        ax2.set_title('Word Count Box Plot')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        os.makedirs(output_dir, exist_ok=True)
        filename = f"word_count_distribution_{APP_CONFIG['user_login']}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=VIS_CONFIG['dpi'], bbox_inches='tight')
        plt.close()
        
        print(f"📊 Word count distribution chart saved: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error creating word count chart: {e}")
        return ""

def create_ml_classification_charts(results_df: pd.DataFrame, output_dir: str = "analysis_outputs") -> str:
    """Create ML classification visualization charts"""
    if results_df.empty or 'ml_cluster' not in results_df.columns:
        print("❌ No ML classification data for visualization")
        return ""
    
    configure_matplotlib()
    
    try:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Cluster distribution
        cluster_counts = results_df['ml_cluster'].value_counts().sort_index()
        ax1.bar(cluster_counts.index, cluster_counts.values, 
               color=VIS_CONFIG['colors']['secondary'], alpha=0.7)
        ax1.set_xlabel('Cluster ID')
        ax1.set_ylabel('Number of Records')
        ax1.set_title('ML Cluster Distribution')
        ax1.grid(True, alpha=0.3)
        
        # Word count by cluster
        for cluster_id in results_df['ml_cluster'].unique():
            cluster_data = results_df[results_df['ml_cluster'] == cluster_id]
            ax2.scatter(cluster_data['ml_cluster'], cluster_data['word_count'], 
                       alpha=0.6, label=f'Cluster {cluster_id}')
        ax2.set_xlabel('Cluster ID')
        ax2.set_ylabel('Word Count')
        ax2.set_title('Word Count by Cluster')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Character count by cluster  
        for cluster_id in results_df['ml_cluster'].unique():
            cluster_data = results_df[results_df['ml_cluster'] == cluster_id]
            ax3.scatter(cluster_data['ml_cluster'], cluster_data['character_count'], 
                       alpha=0.6, label=f'Cluster {cluster_id}')
        ax3.set_xlabel('Cluster ID')
        ax3.set_ylabel('Character Count')
        ax3.set_title('Character Count by Cluster')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Rule-based vs ML clustering
        if 'rule_category' in results_df.columns:
            category_cluster = pd.crosstab(results_df['rule_category'], results_df['ml_cluster'])
            im = ax4.imshow(category_cluster.values, cmap='Blues', aspect='auto')
            ax4.set_xticks(range(len(category_cluster.columns)))
            ax4.set_xticklabels(category_cluster.columns)
            ax4.set_yticks(range(len(category_cluster.index)))
            ax4.set_yticklabels(category_cluster.index, rotation=45)
            ax4.set_xlabel('ML Cluster')
            ax4.set_ylabel('Rule-based Category')
            ax4.set_title('Rule-based vs ML Clustering')
            plt.colorbar(im, ax=ax4)
        
        plt.tight_layout()
        
        os.makedirs(output_dir, exist_ok=True)
        filename = f"ml_classification_analysis_{APP_CONFIG['user_login']}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=VIS_CONFIG['dpi'], bbox_inches='tight')
        plt.close()
        
        print(f"📊 ML classification charts saved: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error creating ML charts: {e}")
        return ""

def create_comprehensive_dashboard(results_df: pd.DataFrame, output_dir: str = "analysis_outputs") -> str:
    """Create comprehensive analysis dashboard"""
    if results_df.empty:
        print("❌ No data for comprehensive dashboard")
        return ""
    
    configure_matplotlib()
    
    try:
        fig = plt.figure(figsize=(20, 15))
        
        # Main title
        fig.suptitle('Thai Voice Recorder - Comprehensive Analysis Dashboard', 
                    fontsize=16, fontweight='bold')
        
        # Dataset overview
        ax1 = plt.subplot(3, 4, 1)
        overview_data = [
            len(results_df),
            results_df['word_count'].sum(),
            results_df['character_count'].sum(),
            len(results_df['ml_cluster'].unique()) if 'ml_cluster' in results_df.columns else 0
        ]
        overview_labels = ['Records', 'Total Words', 'Total Chars', 'Clusters']
        bars = ax1.bar(range(len(overview_data)), overview_data, 
                      color=VIS_CONFIG['colors']['accent'], alpha=0.7)
        ax1.set_xticks(range(len(overview_labels)))
        ax1.set_xticklabels(overview_labels, rotation=45)
        ax1.set_title('Dataset Overview')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, overview_data):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value}', ha='center', va='bottom')
        
        # Word count distribution
        ax2 = plt.subplot(3, 4, 2)
        ax2.hist(results_df['word_count'], bins=15, 
                color=VIS_CONFIG['colors']['primary'], alpha=0.7)
        ax2.set_xlabel('Word Count')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Word Count Distribution')
        ax2.grid(True, alpha=0.3)
        
        # Character count distribution
        ax3 = plt.subplot(3, 4, 3)
        ax3.hist(results_df['character_count'], bins=15, 
                color=VIS_CONFIG['colors']['secondary'], alpha=0.7)
        ax3.set_xlabel('Character Count')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Character Count Distribution')
        ax3.grid(True, alpha=0.3)
        
        # ML Cluster distribution
        if 'ml_cluster' in results_df.columns:
            ax4 = plt.subplot(3, 4, 4)
            cluster_counts = results_df['ml_cluster'].value_counts().sort_index()
            ax4.pie(cluster_counts.values, labels=[f'Cluster {i}' for i in cluster_counts.index], 
                   autopct='%1.1f%%', colors=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow'])
            ax4.set_title('ML Cluster Distribution')
        
        # Statistics summary
        ax5 = plt.subplot(3, 4, (5, 8))
        ax5.axis('off')
        
        stats_text = f"""
DATASET STATISTICS
{'='*30}
Total Records: {len(results_df)}
Total Words: {results_df['word_count'].sum():,}
Total Characters: {results_df['character_count'].sum():,}

WORD STATISTICS
Mean Words: {results_df['word_count'].mean():.1f}
Median Words: {results_df['word_count'].median():.1f}
Std Words: {results_df['word_count'].std():.1f}
Min/Max Words: {results_df['word_count'].min()}/{results_df['word_count'].max()}

CHARACTER STATISTICS  
Mean Characters: {results_df['character_count'].mean():.1f}
Median Characters: {results_df['character_count'].median():.1f}
Std Characters: {results_df['character_count'].std():.1f}
Min/Max Characters: {results_df['character_count'].min()}/{results_df['character_count'].max()}
"""
        
        if 'ml_cluster' in results_df.columns:
            silhouette_score = getattr(results_df, 'attrs', {}).get('silhouette_score', 0.0)
            stats_text += f"""
ML ANALYSIS
Clusters: {len(results_df['ml_cluster'].unique())}
Silhouette Score: {silhouette_score:.3f}
Quality: {'Good' if silhouette_score > 0.3 else 'Moderate' if silhouette_score > 0.1 else 'Low'}
"""
        
        stats_text += f"""
{'='*30}
Generated: {APP_CONFIG['current_datetime']}
User: {APP_CONFIG['user_login']}
"""
        
        ax5.text(0.1, 0.9, stats_text, transform=ax5.transAxes, 
                fontsize=11, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        # Word vs Character scatter
        ax6 = plt.subplot(3, 4, 9)
        if 'ml_cluster' in results_df.columns:
            colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            for i, cluster_id in enumerate(results_df['ml_cluster'].unique()):
                cluster_data = results_df[results_df['ml_cluster'] == cluster_id]
                ax6.scatter(cluster_data['word_count'], cluster_data['character_count'], 
                          alpha=0.6, c=colors[i % len(colors)], label=f'Cluster {cluster_id}')
            ax6.legend()
        else:
            ax6.scatter(results_df['word_count'], results_df['character_count'], alpha=0.6)
        ax6.set_xlabel('Word Count')
        ax6.set_ylabel('Character Count')
        ax6.set_title('Word vs Character Count')
        ax6.grid(True, alpha=0.3)
        
        # Record length categories
        ax7 = plt.subplot(3, 4, 10)
        short_count = len(results_df[results_df['word_count'] <= 5])
        medium_count = len(results_df[(results_df['word_count'] > 5) & (results_df['word_count'] <= 20)])
        long_count = len(results_df[results_df['word_count'] > 20])
        
        categories = ['Short (≤5)', 'Medium (6-20)', 'Long (>20)']
        counts = [short_count, medium_count, long_count]
        
        ax7.bar(categories, counts, color=['lightcoral', 'lightyellow', 'lightgreen'], alpha=0.7)
        ax7.set_ylabel('Number of Records')
        ax7.set_title('Recording Length Categories')
        ax7.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, count in enumerate(counts):
            ax7.text(i, count, f'{count}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        os.makedirs(output_dir, exist_ok=True)
        filename = f"comprehensive_dashboard_{APP_CONFIG['user_login']}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=VIS_CONFIG['dpi'], bbox_inches='tight')
        plt.close()
        
        print(f"📊 Comprehensive dashboard saved: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error creating comprehensive dashboard: {e}")
        return ""