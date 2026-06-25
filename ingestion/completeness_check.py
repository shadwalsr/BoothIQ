import os
import pandas as pd
from pathlib import Path

def run_completeness_check(df_master: pd.DataFrame, data_dir: str):
    """
    Computes completeness metrics based on the master constituencies dataframe.
    """
    total = len(df_master)
    if total == 0:
        print("No constituencies found.")
        return
        
    has_census = df_master['has_census_match'].sum()
    has_scheme = df_master['has_scheme_match'].sum()
    has_news = df_master['has_news_articles'].sum()
    has_nfhs = df_master['has_nfhs_match'].sum() if 'has_nfhs_match' in df_master.columns else 0
    
    # We assume both years are present if they were merged, but let's check
    # Since we use 2025 as base, all have 2025. 
    # 'ac_name_norm_2020' will be non-null if 2020 was present
    has_2020 = df_master['ac_name_norm_2020'].notna().sum()
    
    metrics = {
        'total_constituencies': total,
        'census_match_pct': (has_census / total) * 100,
        'scheme_match_pct': (has_scheme / total) * 100,
        'nfhs_match_pct': (has_nfhs / total) * 100,
        'news_match_pct': (has_news / total) * 100,
        'both_years_pct': (has_2020 / total) * 100
    }
    
    print("\n--- Completeness Report ---")
    for k, v in metrics.items():
        if 'pct' in k:
            print(f"{k}: {v:.2f}%")
        else:
            print(f"{k}: {v}")
            
    out_dir = Path(data_dir) / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(out_dir / "completeness_report.csv", index=False)
    
    if any(v < 95.0 for k, v in metrics.items() if 'pct' in k):
        print("\nWARNING: One or more completeness metrics are below 95%.")
    else:
        print("\nSUCCESS: All completeness metrics are >= 95%.")

