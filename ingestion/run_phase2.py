import os
import json
import pandas as pd
from pathlib import Path
from fuzzy_match import run_fuzzy_match
from join_census import load_census_data
from join_schemes import load_schemes_data
from tag_news import process_news_data
from load_supabase import get_supabase_client, load_constituencies, load_election_results, load_turnout, load_census, load_schemes, load_news
from completeness_check import run_completeness_check
from normalize import normalize_constituency_name

def load_full_eci_data(year: int, data_dir: str) -> pd.DataFrame:
    year_dir = Path(data_dir) / f"raw/eci_{year}"
    records = []
    if not year_dir.exists():
        return pd.DataFrame()
    for file_path in year_dir.glob("*.jsonl"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                # Ensure candidates is a list/jsonb
                if 'candidates' in record:
                    record['candidates'] = json.dumps(record['candidates'])
                records.append(record)
    return pd.DataFrame(records).sort_values('ac_no')

def main():
    base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    
    print("1. Running Fuzzy Match validation (2025 vs 2020)")
    run_fuzzy_match(base_data_dir)
    
    print("\n2. Loading Full Datasets")
    df_eci_2025 = load_full_eci_data(2025, base_data_dir)
    df_eci_2020 = load_full_eci_data(2020, base_data_dir)
    df_census = load_census_data(base_data_dir)
    df_schemes = load_schemes_data(base_data_dir)
    df_news = process_news_data(base_data_dir)
    
    print("\n3. Building Master Constituencies Table")
    # Base from 2025
    df_master = df_eci_2025[['ac_no', 'ac_name']].copy()
    df_master['ac_name_normalized'] = df_master['ac_name'].apply(normalize_constituency_name)
    
    # We don't have district in ECI natively, but we can get it from census or schemes
    if not df_census.empty:
        df_master = df_master.merge(df_census[['ac_no', 'mapped_district_2011']], on='ac_no', how='left')
        df_master.rename(columns={'mapped_district_2011': 'district'}, inplace=True)
    else:
        df_master['district'] = None
        
    df_master['state'] = 'Bihar'
    df_master['area_sq_km'] = None # Spatial data later
    
    # Compute flags
    df_master['has_census_match'] = df_master['ac_no'].isin(df_census['ac_no']) if not df_census.empty else False
    df_master['has_scheme_match'] = df_master['ac_no'].isin(df_schemes['ac_no']) if not df_schemes.empty else False
    
    if not df_news.empty:
        news_ac_counts = df_news.groupby('ac_no').size()
        df_master['has_news_articles'] = df_master['ac_no'].isin(news_ac_counts.index)
    else:
        df_master['has_news_articles'] = False
        
    # Check 2020 presence for completeness
    df_master['ac_name_norm_2020'] = df_master['ac_no'].isin(df_eci_2020['ac_no'])
    
    print("\n4. Running Completeness Check")
    run_completeness_check(df_master, base_data_dir)
    
    print("\n5. Computing Turnout")
    df_turnout = pd.DataFrame()
    if not df_eci_2025.empty and not df_eci_2020.empty:
        t_2025 = df_eci_2025[['ac_no', 'voter_turnout_pct', 'total_electors']].rename(columns={'voter_turnout_pct': 'turnout_2025_pct', 'total_electors': 'electors_2025'})
        t_2020 = df_eci_2020[['ac_no', 'voter_turnout_pct', 'total_electors']].rename(columns={'voter_turnout_pct': 'turnout_2020_pct', 'total_electors': 'electors_2020'})
        df_turnout = pd.merge(t_2025, t_2020, on='ac_no', how='outer')
        df_turnout['turnout_delta'] = df_turnout['turnout_2025_pct'] - df_turnout['turnout_2020_pct']

    print("\n6. Loading to Supabase")
    try:
        supabase = get_supabase_client()
        
        print("  - constituencies")
        # Drop temporary col before insert
        df_master_db = df_master.drop(columns=['ac_name_norm_2020'])
        load_constituencies(df_master_db, supabase)
        
        if not df_eci_2025.empty:
            print("  - election_results_2025")
            load_election_results(df_eci_2025, 2025, supabase)
            
        if not df_eci_2020.empty:
            print("  - election_results_2020")
            load_election_results(df_eci_2020, 2020, supabase)
            
        if not df_turnout.empty:
            print("  - turnout")
            load_turnout(df_turnout, supabase)
            
        if not df_census.empty:
            print("  - census_demographics")
            load_census(df_census, supabase)
            
        if not df_schemes.empty:
            print("  - schemes")
            load_schemes(df_schemes, supabase)
            
        if not df_news.empty:
            print("  - news_articles")
            # Filter only those with assigned ac_no for the foreign key, or nullable
            # Schema says nullable, but we'll insert them all
            load_news(df_news, supabase)
            
        print("Done!")
    except Exception as e:
        print(f"Error loading to Supabase: {e}")

if __name__ == "__main__":
    main()
