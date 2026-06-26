import os
import sys
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from load_supabase import get_supabase_client, load_election_results, load_turnout
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
    load_dotenv()
    base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    
    print("1. Loading ECI 2025 and 2020 datasets...")
    df_eci_2025 = load_full_eci_data(2025, base_data_dir)
    df_eci_2020 = load_full_eci_data(2020, base_data_dir)
    
    print(f"Loaded {len(df_eci_2025)} rows for 2025.")
    print(f"Loaded {len(df_eci_2020)} rows for 2020.")
    
    print("\n2. Computing Turnout...")
    t_2025 = df_eci_2025[['ac_no', 'voter_turnout_pct', 'total_electors']].rename(columns={'voter_turnout_pct': 'turnout_2025_pct', 'total_electors': 'electors_2025'})
    t_2020 = df_eci_2020[['ac_no', 'voter_turnout_pct', 'total_electors']].rename(columns={'voter_turnout_pct': 'turnout_2020_pct', 'total_electors': 'electors_2020'})
    df_turnout = pd.merge(t_2025, t_2020, on='ac_no', how='outer')
    df_turnout['turnout_delta'] = df_turnout['turnout_2025_pct'] - df_turnout['turnout_2020_pct']
    print(f"Turnout computed: {len(df_turnout)} rows.")
    
    print("\n3. Connecting to Supabase and uploading...")
    supabase = get_supabase_client()
    
    print("  - election_results_2025")
    load_election_results(df_eci_2025, 2025, supabase)
    
    print("  - election_results_2020")
    load_election_results(df_eci_2020, 2020, supabase)
    
    print("  - turnout")
    load_turnout(df_turnout, supabase)
    
    print("\nUpload complete! ECI results and turnout updated successfully.")

if __name__ == "__main__":
    main()
