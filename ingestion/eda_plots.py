import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def generate_plots(df: pd.DataFrame, output_dir: str):
    """
    Generates and saves the EDA plots:
    1. Correlation Heatmap
    2. Hypothesis Scatter Plots (with Pearson r and sanity check warnings)
    3. Distribution Histograms for key features
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Correlation Heatmap
    # Filter for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Exclude id and ac_no if present
    cols_for_corr = [c for c in numeric_cols if c not in ['id', 'ac_no']]
    
    if len(cols_for_corr) > 1:
        plt.figure(figsize=(16, 12))
        corr = df[cols_for_corr].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(
            corr, 
            mask=mask, 
            annot=True, 
            fmt=".2f", 
            cmap='coolwarm', 
            vmin=-1, 
            vmax=1, 
            square=True, 
            linewidths=.5,
            cbar_kws={"shrink": .8}
        )
        plt.title('Constituency Features Correlation Heatmap', fontsize=18, fontweight='bold', pad=20)
        plt.tight_layout()
        heatmap_path = os.path.join(output_dir, 'correlation_heatmap.png')
        plt.savefig(heatmap_path, dpi=300)
        plt.close()
        print(f"Saved correlation heatmap to {heatmap_path}")
    
    # 2. Hypothesis Scatter Plots
    # Format: (x_col, y_col, expected_dir, description)
    # expected_dir is 'positive' or 'negative' or 'weak_positive'
    hypotheses = [
        ('literacy_rate_normalized', 'turnout_delta', 'positive', 'literacy vs turnout delta'),
        ('scheme_penetration_score', 'vote_share_swing', 'positive', 'scheme penetration vs vote swing'),
        ('urbanization_pct', 'competitiveness_score', 'positive', 'urbanization vs competitiveness'),
        ('agriculture_dependency_pct', 'mgnrega_penetration_pct', 'positive', 'ag dependency vs mgnrega penetration'),
        ('sc_st_pct', 'turnout_delta', 'positive', 'SC/ST pct vs turnout delta'),
        ('religion_diversity_index', 'competitiveness_score', 'positive', 'religion diversity vs competitiveness')
    ]
    
    for x_col, y_col, expected, desc in hypotheses:
        if x_col not in df.columns or y_col not in df.columns:
            print(f"Skipping plot {desc}: column {x_col} or {y_col} not found in DataFrame.")
            continue
            
        # Drop NaNs for correlation calculation
        valid_data = df[[x_col, y_col]].dropna()
        if len(valid_data) < 2:
            continue
            
        r = valid_data[x_col].corr(valid_data[y_col])
        
        # Plot
        plt.figure(figsize=(8, 6))
        sns.regplot(data=valid_data, x=x_col, y=y_col, scatter_kws={'alpha':0.6, 'color':'#2c3e50'}, line_kws={'color':'#e74c3c'})
        plt.title(f"{desc.title()}\nPearson r = {r:.2f}", fontsize=14, fontweight='bold', pad=10)
        plt.xlabel(x_col.replace('_', ' ').title())
        plt.ylabel(y_col.replace('_', ' ').title())
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        
        plot_name = f"scatter_{x_col}_vs_{y_col}.png"
        plot_path = os.path.join(output_dir, plot_name)
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"Saved scatter plot to {plot_path}")
        
        # Sanity checking
        # Red flag if correlation magnitude > 0.3 in the opposite direction of political sanity
        if expected == 'positive' and r < -0.3:
            print(f"WARNING: Politically implausible correlation in {desc}! "
                  f"Expected positive, found strong negative (r = {r:.2f}). "
                  f"Please inspect the data joins and feature calculation.")
        elif expected == 'negative' and r > 0.3:
            print(f"WARNING: Politically implausible correlation in {desc}! "
                  f"Expected negative, found strong positive (r = {r:.2f}). "
                  f"Please inspect the data joins and feature calculation.")
            
    # 3. Distribution Histograms
    cols_to_hist = [
        'turnout_delta', 'vote_share_swing', 'margin_pct_2025', 
        'competitiveness_score', 'effective_candidates', 'anti_incumbency_magnitude',
        'literacy_rate_normalized', 'urbanization_pct', 'sc_st_pct',
        'agriculture_dependency_pct', 'religion_diversity_index', 'scheme_penetration_score'
    ]
    
    for col in cols_to_hist:
        if col in df.columns:
            plt.figure(figsize=(8, 5))
            sns.histplot(df[col].dropna(), kde=True, color='#34495e', bins=30)
            plt.title(f"Distribution of {col.replace('_', ' ').title()}", fontsize=14, fontweight='bold')
            plt.xlabel(col.replace('_', ' ').title())
            plt.ylabel('Count')
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            
            hist_name = f"dist_{col}.png"
            hist_path = os.path.join(output_dir, hist_name)
            plt.savefig(hist_path, dpi=150)
            plt.close()
            print(f"Saved distribution plot to {hist_path}")
            
    print("EDA plot generation complete.")
