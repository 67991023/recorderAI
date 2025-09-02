"""
Data Visualization Functions (No Time Analysis)
==============================================
Author: User 67991023
Current Date and Time (UTC): 2025-08-28 06:51:14
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import os
from config import VIS_CONFIG, APP_CONFIG

# Check for seaborn availability
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
            print(f"✅ Using font: {selected_font}")
        else:
            plt.rcParams['font.family'] = ['sans-serif']
            print("⚠️ Using default font")
            
    except Exception as e:
        print(f"⚠️ Font configuration error: {e}")
        plt.rcParams['font.family'] = ['sans-serif']

def create_word_count_distribution_chart(voice_records: List[Dict], output_dir: str = "analysis_outputs") -> str:
    """
    Create word count distribution visualization
    
    Args:
        voice_records: List of voice records
        output_dir: Output directory
        
    Returns:
        str: Path to saved chart
    """
    from text_processing import fix_thai_word_count
    
    if not voice_records:
        print("❌ No data for word count distribution")
        return ""
    
    print(f"📊 Creating word count distribution chart for {len(voice_records)} records...")
    
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
        ax.axvline(mean_words, color='red', linestyle='--', linewidth=2,
                  label=f'Mean: {mean_words:.1f}')
        ax.axvline(median_words, color='green', linestyle='--', linewidth=2,
                  label=f'Median: {median_words:.1f}')
        
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
    """
    Create ML classification visualization charts
    
    Args:
        results_df: DataFrame with ML results
        output_dir: Output directory
        
    Returns:
        str: Path to saved chart
    """
    if results_df.empty:
        print("❌ No data for ML classification charts")
        return ""
    
    print("🤖 Creating ML classification charts...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Machine Learning Classification Analysis', fontsize=16, y=0.98)
        
        # 1. ML Clusters
        if 'ml_cluster' in results_df.columns and len(results_df['ml_cluster'].unique()) > 1:
            cluster_counts = results_df['ml_cluster'].value_counts().sort_index()
            colors = plt.cm.Set3(np.linspace(0, 1, len(cluster_counts)))
            bars = ax1.bar(range(len(cluster_counts)), cluster_counts.values, 
                          color=colors, alpha=0.8, edgecolor='black')
            ax1.set_title('ML Clusters (K-Means)', fontsize=12)
            ax1.set_xlabel('Cluster ID')
            ax1.set_ylabel('Records Count')
            ax1.set_xticks(range(len(cluster_counts)))
            ax1.set_xticklabels([f'C{i}' for i in cluster_counts.index])
            
            # Add silhouette score if available
            if hasattr(results_df, 'attrs') and 'silhouette_score' in results_df.attrs:
                silhouette = results_df.attrs['silhouette_score']
                ax1.text(0.02, 0.98, f'Silhouette Score: {silhouette:.3f}', 
                        transform=ax1.transAxes, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
        else:
            ax1.text(0.5, 0.5, 'Single Cluster\n(Insufficient data)', 
                    ha='center', va='center', transform=ax1.transAxes,
                    bbox=dict(boxstyle='round', facecolor='lightgray'))
            ax1.set_title('ML Clusters', fontsize=12)
        
        # 2. Rule-based Categories
        if 'rule_category' in results_df.columns:
            category_counts = results_df['rule_category'].value_counts()
            colors = plt.cm.Pastel1(np.linspace(0, 1, len(category_counts)))
            wedges, texts, autotexts = ax2.pie(
                category_counts.values, 
                labels=[cat[:15] + '...' if len(cat) > 15 else cat for cat in category_counts.index],
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            ax2.set_title('Rule-based Categories', fontsize=12)
        
        # 3. Word Count by Cluster
        if 'ml_cluster' in results_df.columns and len(results_df['ml_cluster'].unique()) > 1:
            clusters = results_df['ml_cluster'].unique()
            cluster_word_data = [results_df[results_df['ml_cluster'] == c]['word_count'].values for c in clusters]
            
            box_plot = ax3.boxplot(cluster_word_data, labels=[f'C{c}' for c in clusters], patch_artist=True)
            ax3.set_title('Word Count by Cluster', fontsize=12)
            ax3.set_ylabel('Word Count')
            ax3.grid(True, alpha=0.3)
            
            # Color the boxes
            colors = plt.cm.Set2(np.linspace(0, 1, len(clusters)))
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
        else:
            word_counts = results_df['word_count']
            ax3.hist(word_counts, bins=min(10, len(word_counts)), alpha=0.7, 
                    color=VIS_CONFIG['colors']['secondary'], edgecolor='black')
            ax3.set_title('Word Count Distribution', fontsize=12)
            ax3.set_xlabel('Word Count')
            ax3.set_ylabel('Frequency')
            ax3.grid(True, alpha=0.3)
        
        # 4. Cluster vs Category Heatmap
        if ('ml_cluster' in results_df.columns and 'rule_category' in results_df.columns 
            and len(results_df['ml_cluster'].unique()) > 1):
            
            cluster_rule_crosstab = pd.crosstab(results_df['ml_cluster'], results_df['rule_category'])
            
            if SEABORN_AVAILABLE:
                sns.heatmap(cluster_rule_crosstab, annot=True, cmap='Blues', ax=ax4)
            else:
                im = ax4.imshow(cluster_rule_crosstab.values, cmap='Blues', aspect='auto')
                
                # Add values to heatmap
                for i in range(len(cluster_rule_crosstab.index)):
                    for j in range(len(cluster_rule_crosstab.columns)):
                        ax4.text(j, i, cluster_rule_crosstab.iloc[i, j],
                               ha="center", va="center", 
                               color="black" if cluster_rule_crosstab.iloc[i, j] < 2 else "white")
                
                ax4.set_xticks(range(len(cluster_rule_crosstab.columns)))
                ax4.set_xticklabels([cat[:10] + '...' if len(cat) > 10 else cat 
                                   for cat in cluster_rule_crosstab.columns], rotation=45)
                ax4.set_yticks(range(len(cluster_rule_crosstab.index)))
                ax4.set_yticklabels([f'C{i}' for i in cluster_rule_crosstab.index])
            
            ax4.set_title('ML Clusters vs Rule Categories', fontsize=12)
            ax4.set_xlabel('Rule Categories')
            ax4.set_ylabel('ML Clusters')
        else:
            ax4.text(0.5, 0.5, 'Cluster-Category\nAnalysis\nNot Available', 
                    ha='center', va='center', transform=ax4.transAxes,
                    bbox=dict(boxstyle='round', facecolor='lightgray'))
        
        plt.tight_layout()
        
        output_file = f'{output_dir}/ml_classification_analysis.png'
        plt.savefig(output_file, dpi=VIS_CONFIG['dpi'], bbox_inches='tight', facecolor='white')
        
        print(f"✅ ML classification charts saved: {output_file}")
        plt.show()
        
        return output_file
        
    except Exception as e:
        print(f"❌ ML classification charts error: {e}")
        return ""

def create_comprehensive_dashboard(results_df: pd.DataFrame, output_dir: str = "analysis_outputs") -> str:
    """
    Create comprehensive analysis dashboard (without time series)
    
    Args:
        results_df: DataFrame with ML results
        output_dir: Output directory
        
    Returns:
        str: Path to saved dashboard
    """
    if results_df.empty:
        print("❌ No data for comprehensive dashboard")
        return ""
    
    print("📊 Creating comprehensive analysis dashboard...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle(f'Thai Voice Data Analysis Dashboard\n'
                    f'User: {APP_CONFIG["user_login"]} | Analysis Time: {APP_CONFIG["current_datetime"]}', 
                    fontsize=14, y=0.96)
        
        # 1. Word Count Distribution
        ax1 = plt.subplot(2, 3, 1)
        word_counts = results_df['word_count'].values
        n_bins = min(15, len(word_counts))
        counts, bins, patches = ax1.hist(word_counts, bins=n_bins, alpha=0.7, 
                                       color=VIS_CONFIG['colors']['primary'], 
                                       edgecolor='navy')
        
        mean_words = np.mean(word_counts)
        ax1.axvline(mean_words, color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {mean_words:.1f}')
        ax1.set_title('Word Count Distribution', fontsize=12)
        ax1.set_xlabel('Words per Record')
        ax1.set_ylabel('Frequency')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. ML Clusters
        ax2 = plt.subplot(2, 3, 2)
        if 'ml_cluster' in results_df.columns and len(results_df['ml_cluster'].unique()) > 1:
            cluster_counts = results_df['ml_cluster'].value_counts().sort_index()
            bars = ax2.bar(range(len(cluster_counts)), cluster_counts.values, 
                          color=plt.cm.Set3(np.linspace(0, 1, len(cluster_counts))), alpha=0.8)
            ax2.set_title('ML Clusters', fontsize=12)
            ax2.set_xlabel('Cluster ID')
            ax2.set_ylabel('Count')
            ax2.set_xticks(range(len(cluster_counts)))
            ax2.set_xticklabels([f'C{i}' for i in cluster_counts.index])
        else:
            ax2.text(0.5, 0.5, 'Single Cluster', ha='center', va='center', 
                    transform=ax2.transAxes, bbox=dict(boxstyle='round', facecolor='lightgray'))
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
        
        # Add correlation
        if len(results_df) > 1:
            corr = np.corrcoef(results_df['word_count'], results_df['character_count'])[0, 1]
            ax4.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                    transform=ax4.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # 5. Category Word Counts
        ax5 = plt.subplot(2, 3, 5)
        if 'rule_category' in results_df.columns:
            cat_word_means = results_df.groupby('rule_category')['word_count'].mean().sort_values(ascending=False)
            bars = ax5.bar(range(len(cat_word_means)), cat_word_means.values, 
                          alpha=0.7, color='steelblue')
            ax5.set_title('Avg Words by Category', fontsize=12)
            ax5.set_ylabel('Average Words')
            ax5.set_xticks(range(len(cat_word_means)))
            ax5.set_xticklabels([cat[:8] + '...' if len(cat) > 8 else cat 
                               for cat in cat_word_means.index], rotation=45)
            ax5.grid(True, alpha=0.3)
        
        # 6. Statistics Summary
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        total_records = len(results_df)
        total_words = results_df['word_count'].sum()
        avg_words = results_df['word_count'].mean()
        std_words = results_df['word_count'].std()
        
        stats_text = f"""📊 ANALYSIS SUMMARY
{'='*25}

📈 Dataset Overview:
• Total Records: {total_records:,}
• Total Words: {total_words:,}
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
                fontsize=9, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.2))
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        
        output_file = f'{output_dir}/comprehensive_dashboard.png'
        plt.savefig(output_file, dpi=VIS_CONFIG['dpi'], bbox_inches='tight', facecolor='white')
        
        print(f"✅ Comprehensive dashboard saved: {output_file}")
        plt.show()
        
        return output_file
        
    except Exception as e:
        print(f"❌ Comprehensive dashboard error: {e}")
        return ""