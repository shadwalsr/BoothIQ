import os
import sys
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Ensure script can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from load_supabase import get_supabase_client

def run_phase5():
    load_dotenv()
    
    print("Connecting to Supabase...")
    try:
        supabase = get_supabase_client()
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        sys.exit(1)
        
    print("Fetching constituency features...")
    try:
        res = supabase.table('constituency_features').select('*').execute()
        df = pd.DataFrame(res.data)
        print(f"Loaded {len(df)} constituency features.")
    except Exception as e:
        print(f"Error fetching features: {e}")
        sys.exit(1)
        
    assert len(df) == 243, f"Expected 243 rows, found {len(df)}"
    
    # 1. Select feature set for clustering
    features = [
        # Electoral
        'turnout_delta', 'vote_share_swing', 'margin_pct_2025', 'margin_pct_delta',
        'competitiveness_score', 'effective_candidates', 'anti_incumbency_magnitude',
        # Demographic
        'literacy_rate_normalized', 'urbanization_pct', 'sc_st_pct', 'agriculture_dependency_pct',
        'religion_diversity_index', 'religion_hindu_pct', 'religion_muslim_pct',
        # Welfare
        'scheme_penetration_score', 
        'nfhs_households_with_electricity_pct', 'nfhs_households_with_improved_drinking_water_source_pct',
        'nfhs_households_using_improved_sanitation_facility_pct', 'nfhs_women_who_are_literate_pct',
        'nfhs_children_under_5_years_who_are_stunted_pct',
        # Discourse
        'discourse_pct_inflation', 'discourse_pct_communal', 'discourse_pct_development',
        'discourse_pct_welfare', 'discourse_pct_caste', 'discourse_pct_unemployment',
        'discourse_pct_other'
    ]
    
    print(f"Clustering on {len(features)} features.")
    X = df[features].copy()
    
    # Impute missing values for discourse columns (sparse constituencies) using column mean
    discourse_cols = [c for c in features if c.startswith('discourse_pct_')]
    for col in discourse_cols:
        col_mean = X[col].mean()
        # Handle case where entire column might be NaN (fallback to 0.0)
        if pd.isna(col_mean):
            col_mean = 0.0
        X[col] = X[col].fillna(col_mean)
        
    # Double-check that no NaNs remain
    nan_counts = X.isnull().sum()
    if nan_counts.sum() > 0:
        print("WARNING: Found NaNs in feature matrix after imputation:")
        print(nan_counts[nan_counts > 0])
        X = X.fillna(0.0)
        
    # 2. Standardize features
    print("Standardizing features with StandardScaler...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 3. Fit K-means with K=6 (random_state=42 for reproducibility)
    k = 6
    print(f"Fitting K-means with K={k} (seed=42)...")
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    
    df['cluster_id'] = labels
    print("Cluster sizes:")
    print(df['cluster_id'].value_counts().sort_index())
    
    # 4. Write cluster_id back to constituency_features
    print("Uploading cluster_id assignments to constituency_features table...")
    update_records = df[['ac_no', 'cluster_id']].to_dict(orient="records")
    # Ensure types are correct
    for r in update_records:
        r['ac_no'] = int(r['ac_no'])
        r['cluster_id'] = int(r['cluster_id'])
        
    try:
        supabase.table('constituency_features').upsert(update_records, on_conflict='ac_no').execute()
        print("Successfully updated cluster_id for all 243 constituencies in constituency_features!")
    except Exception as e:
        print(f"Error uploading cluster_id: {e}")
        sys.exit(1)
        
    # 5. Populate cluster_personas table
    personas = [
        {
            "cluster_id": 0,
            "persona_name": "Welfare-Satisfied Incumbent Strongholds",
            "description": "Deeply rural, high-welfare penetration seats with strong pro-incumbent swings and comfortable winning margins."
        },
        {
            "cluster_id": 1,
            "persona_name": "Welfare-Exposed Stagnant Seats",
            "description": "Rural seats with high welfare delivery but experiencing turnout drops and flat swings, indicating voter complacency."
        },
        {
            "cluster_id": 2,
            "persona_name": "Marginalized Minority Belt",
            "description": "Low-literacy rural seats with very high Muslim population shares and low welfare penetration, showing moderate swing."
        },
        {
            "cluster_id": 3,
            "persona_name": "Rural Campaign-Driven Belts",
            "description": "Rural constituencies with average literacy and low scheme exposure, where news is dominated by general campaign rallies rather than local developmental issues."
        },
        {
            "cluster_id": 4,
            "persona_name": "Aspirational Urban Centers",
            "description": "Highly urbanized and literate constituencies focused on employment, youth issues, and infrastructure, with narrow margins."
        },
        {
            "cluster_id": 5,
            "persona_name": "High-Volatility Battlegrounds",
            "description": "Rural, literate constituencies characterized by negative swing, thin winning margins, and high youth unemployment concern, making them primary swing targets."
        }
    ]
    
    print("Uploading personas to cluster_personas table...")
    try:
        # Use upsert to avoid foreign key violations from referencing tables
        supabase.table('cluster_personas').upsert(personas, on_conflict='cluster_id').execute()
        print("Successfully populated cluster_personas table!")
    except Exception as e:
        print(f"Error populating cluster_personas: {e}")
        sys.exit(1)
        
    print("\nPhase 5 Clustering & Persona Definition completed successfully!")

if __name__ == '__main__':
    run_phase5()
