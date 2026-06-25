import os
import json
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment.")
    return create_client(url, key)

def load_constituencies(df: pd.DataFrame, supabase: Client):
    records = df.to_dict(orient="records")
    # we expect: ac_no, ac_name, ac_name_normalized, district, state, area_sq_km, etc.
    # Replace nan with None
    records = [{k: (v if pd.notna(v) else None) for k, v in r.items()} for r in records]
    supabase.table('constituencies').upsert(records, on_conflict='ac_no').execute()

def load_election_results(df: pd.DataFrame, year: int, supabase: Client):
    table_name = f'election_results_{year}'
    allowed_cols = [
        'ac_no', 'election_year', 'total_electors', 'total_polled_votes',
        'evm_votes', 'postal_votes', 'voter_turnout_pct', 'winner_name',
        'winner_party', 'margin', 'candidates', 'polling_stations_count',
        'rejected_postal_votes', 'nota_votes', 'tendered_votes'
    ]
    df_to_load = df[[c for c in allowed_cols if c in df.columns]].copy()
        
    records = df_to_load.to_dict(orient="records")
    records = [{k: (v if pd.notna(v) else None) for k, v in r.items()} for r in records]
    
    # We want to insert/update, but we don't have a unique constraint on ac_no alone.
    # To be safe, we can just delete for the year and insert
    supabase.table(table_name).delete().eq('election_year', year).execute()
    
    # Batch insert since there might be 243
    # supabase python client handles reasonably large arrays
    supabase.table(table_name).insert(records).execute()

def load_turnout(df: pd.DataFrame, supabase: Client):
    records = df.to_dict(orient="records")
    records = [{k: (v if pd.notna(v) else None) for k, v in r.items()} for r in records]
    # To be safe, delete all and re-insert
    supabase.table('turnout').delete().neq('ac_no', 0).execute() # delete all
    supabase.table('turnout').insert(records).execute()

def load_census(df: pd.DataFrame, supabase: Client):
    records = df.to_dict(orient="records")
    records = [{k: (v if pd.notna(v) else None) for k, v in r.items()} for r in records]
    supabase.table('census_demographics').delete().neq('ac_no', 0).execute()
    supabase.table('census_demographics').insert(records).execute()

def load_schemes(df: pd.DataFrame, supabase: Client):
    records = df.to_dict(orient="records")
    records = [{k: (v if pd.notna(v) else None) for k, v in r.items()} for r in records]
    supabase.table('schemes').delete().neq('ac_no', 0).execute()
    supabase.table('schemes').insert(records).execute()

def load_nfhs(df: pd.DataFrame, supabase: Client):
    records = df.to_dict(orient="records")
    records = [{k: (v if pd.notna(v) else None) for k, v in r.items()} for r in records]
    supabase.table('nfhs_5').delete().neq('ac_no', 0).execute()
    supabase.table('nfhs_5').insert(records).execute()

def load_news(df: pd.DataFrame, supabase: Client):
    records = df.to_dict(orient="records")
    records = [{k: (v if pd.notna(v) else None) for k, v in r.items()} for r in records]
    
    # ensure date format is correct for publishing_date, or None
    for r in records:
        if r.get('publishing_date'):
            r['publishing_date'] = str(r['publishing_date'])
            
    supabase.table('news_articles').delete().neq('id', 0).execute() # delete all
    
    # Insert in chunks of 100 to avoid request size limits
    chunk_size = 100
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i+chunk_size]
        supabase.table('news_articles').insert(chunk).execute()

def load_latest(df: pd.DataFrame, supabase: Client):
    records = df.to_dict(orient="records")
    
    def safe_notna(v):
        if v is None:
            return False
        if isinstance(v, (list, dict)):
            return True
        try:
            return pd.notna(v)
        except Exception:
            return True
            
    records = [{k: (v if safe_notna(v) else None) for k, v in r.items()} for r in records]
    
    for r in records:
        r['ac_no'] = int(r['ac_no'])
        for k in ['infra_total_primary_schools', 'infra_secondary_schools', 'infra_phc_sub_centers',
                  'law_petty_thefts', 'law_communal_friction_cases', 'jeevika_active_shg_groups',
                  'jeevika_bank_linkages_count', 'markets_registered_mandis_count', 'markets_weekly_haats_count',
                  'panchayat_total', 'panchayat_mukhiyas_aligned_nda', 'panchayat_mukhiyas_aligned_grand_alliance',
                  'panchayat_mukhiyas_independent', 'power_local_transformers_count',
                  'sensitivity_historical_incident_hotspots_count']:
            if r.get(k) is not None:
                r[k] = int(r[k])
                
    supabase.table('latest_constituency_data').delete().neq('ac_no', 0).execute()
    
    # Insert in chunks of 50 to avoid request size limits
    chunk_size = 50
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i+chunk_size]
        supabase.table('latest_constituency_data').insert(chunk).execute()


