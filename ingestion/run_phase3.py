import os
import sys
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Ensure the script can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from load_supabase import get_supabase_client
from compute_features import (
    compute_electoral_features,
    compute_demographic_features,
    compute_scheme_features,
    compute_nfhs_features,
    compute_news_discourse_features
)
from eda_plots import generate_plots

def run_pipeline():
    load_dotenv()
    
    print("Connecting to Supabase...")
    try:
        supabase = get_supabase_client()
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        sys.exit(1)
        
    print("\nFetching tables from Supabase...")
    # Fetch election results 2025
    res_2025 = supabase.table('election_results_2025').select('*').execute()
    df_2025 = pd.DataFrame(res_2025.data)
    print(f"Loaded {len(df_2025)} election results from 2025.")
    
    # Fetch election results 2020
    res_2020 = supabase.table('election_results_2020').select('*').execute()
    df_2020 = pd.DataFrame(res_2020.data)
    print(f"Loaded {len(df_2020)} election results from 2020.")
    
    # Fetch census demographics
    res_census = supabase.table('census_demographics').select('*').execute()
    df_census = pd.DataFrame(res_census.data)
    print(f"Loaded {len(df_census)} census records.")
    
    # Fetch schemes
    res_schemes = supabase.table('schemes').select('*').execute()
    df_schemes = pd.DataFrame(res_schemes.data)
    print(f"Loaded {len(df_schemes)} scheme records.")
    
    # Fetch NFHS-5
    res_nfhs = supabase.table('nfhs_5').select('*').execute()
    df_nfhs = pd.DataFrame(res_nfhs.data)
    print(f"Loaded {len(df_nfhs)} NFHS-5 records.")
    
    # Fetch news articles
    print("Fetching news articles from Supabase...")
    all_news = []
    limit = 1000
    offset = 0
    while True:
        res = supabase.table('news_articles').select('id, ac_no').range(offset, offset + limit - 1).execute()
        data = res.data
        if not data:
            break
        all_news.extend(data)
        if len(data) < limit:
            break
        offset += limit
    df_news = pd.DataFrame(all_news)
    print(f"Loaded {len(df_news)} news articles.")
    
    # Validation checks
    assert len(df_2025) == 243, f"Expected 243 rows in 2025 election results, found {len(df_2025)}"
    assert len(df_2020) == 243, f"Expected 243 rows in 2020 election results, found {len(df_2020)}"
    assert len(df_census) == 243, f"Expected 243 rows in census demographics, found {len(df_census)}"
    assert len(df_schemes) == 243, f"Expected 243 rows in schemes, found {len(df_schemes)}"
    assert len(df_nfhs) == 243, f"Expected 243 rows in NFHS-5, found {len(df_nfhs)}"
    
    print("\nComputing features...")
    
    # Electoral features
    print("1. Computing electoral features...")
    df_elec = compute_electoral_features(df_2025, df_2020)
    print(f"Electoral features shape: {df_elec.shape}")
    
    # Demographic features
    print("2. Computing demographic features...")
    df_demo = compute_demographic_features(df_census)
    print(f"Demographic features shape: {df_demo.shape}")
    
    # Scheme features
    print("3. Computing scheme features...")
    df_scheme = compute_scheme_features(df_schemes, df_census)
    print(f"Scheme features shape: {df_scheme.shape}")
    
    # NFHS-5 features
    print("4. Computing NFHS-5 features...")
    df_nfhs_feats = compute_nfhs_features(df_nfhs)
    print(f"NFHS-5 features shape: {df_nfhs_feats.shape}")
    
    # News discourse features
    print("5. Computing news discourse features...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df_discourse = compute_news_discourse_features(df_news, base_dir)
    print(f"Discourse features shape: {df_discourse.shape}")
    
    # Merge all features on ac_no
    print("\nMerging all features...")
    df_features = pd.merge(df_elec, df_demo, on='ac_no')
    df_features = pd.merge(df_features, df_scheme, on='ac_no')
    df_features = pd.merge(df_features, df_nfhs_feats, on='ac_no')
    df_features = pd.merge(df_features, df_discourse, on='ac_no')
    print(f"Final merged features shape: {df_features.shape}")
    
    # Validation of final dataframe
    assert len(df_features) == 243, f"Expected 243 rows in merged features, found {len(df_features)}"
    
    # Assertions on discourse features (exit conditions)
    assert df_features['discourse_data_sparse'].notna().all(), "Found null values in discourse_data_sparse column!"
    assert df_features['discourse_data_sparse'].dtype == bool, f"discourse_data_sparse is not boolean: {df_features['discourse_data_sparse'].dtype}"
    
    # Assertions for sparsity rule
    sparse_rows = df_features[df_features['discourse_data_sparse'] == True]
    non_sparse_rows = df_features[df_features['discourse_data_sparse'] == False]
    
    pct_cols = [f'discourse_pct_{cat}' for cat in ['inflation', 'communal', 'development', 'welfare', 'caste', 'unemployment', 'other']]
    for col in pct_cols:
        assert sparse_rows[col].isna().all(), f"Found non-null values in {col} for sparse constituencies!"
        
    for col in pct_cols:
        assert non_sparse_rows[col].notna().all(), f"Found null values in {col} for non-sparse constituencies!"
        
    sums = non_sparse_rows[pct_cols].sum(axis=1)
    assert np.allclose(sums, 100.0, atol=1e-3), f"Discourse percentages do not sum to 100% for non-sparse rows"
    print(f"Discourse features validation passed: {len(sparse_rows)} sparse, {len(non_sparse_rows)} non-sparse constituencies.")
    
    # Check for NaNs in critical columns
    critical_cols = [
        'turnout_delta', 'vote_share_swing', 'margin_pct_2025',
        'competitiveness_score', 'effective_candidates', 'anti_incumbency_flag',
        'anti_incumbency_magnitude', 'literacy_rate_normalized', 'urbanization_pct',
        'sc_st_pct', 'agriculture_dependency_pct', 'religion_diversity_index',
        'scheme_penetration_score', 'nfhs_households_with_electricity_pct',
        'nfhs_households_with_improved_drinking_water_source_pct',
        'nfhs_households_using_improved_sanitation_facility_pct',
        'nfhs_women_who_are_literate_pct', 'nfhs_children_under_5_years_who_are_stunted_pct'
    ]
    for col in critical_cols:
        nan_count = df_features[col].isna().sum()
        if nan_count > 0:
            print(f"WARNING: Found {nan_count} NaN values in critical column: {col}")
            
    # Spot-check anti-incumbency count
    flipped_count = df_features['anti_incumbency_flag'].sum()
    print(f"Flipped seats count (anti-incumbency flag == 1): {flipped_count}")
    
    # 4. Generate EDA Plots
    print("\nGenerating EDA plots...")
    output_dir = os.path.join(base_dir, "data", "processed", "eda")
    generate_plots(df_features, output_dir)
    
    # 5. Load to Supabase
    print("\nUploading features to Supabase...")
    records = df_features.to_dict(orient="records")
    # Replace nan with None
    records = [{k: (v if pd.notna(v) else None) for k, v in r.items()} for r in records]
    
    # Ensure postgres-friendly types
    for r in records:
        r['ac_no'] = int(r['ac_no'])
        r['anti_incumbency_flag'] = int(r['anti_incumbency_flag'])
        if 'scheme_data_is_district_estimate' in r:
            r['scheme_data_is_district_estimate'] = bool(r['scheme_data_is_district_estimate'])
        if 'discourse_data_sparse' in r:
            r['discourse_data_sparse'] = bool(r['discourse_data_sparse'])
        for cat in ['inflation', 'communal', 'development', 'welfare', 'caste', 'unemployment', 'other']:
            col_name = f'discourse_pct_{cat}'
            if col_name in r and r[col_name] is not None:
                r[col_name] = float(r[col_name])
            
    try:
        supabase.table('constituency_features').upsert(records, on_conflict='ac_no').execute()
        print("Successfully uploaded all 243 constituency features to constituency_features table!")
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        sys.exit(1)
        
    print("\nPhase 3 Feature Engineering pipeline executed successfully!")

if __name__ == "__main__":
    run_pipeline()
