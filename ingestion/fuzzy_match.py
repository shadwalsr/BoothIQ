import json
import os
import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz
from normalize import normalize_constituency_name

def load_eci_names(year: int, data_dir: str) -> pd.DataFrame:
    """Loads ECI JSONL files and returns a DataFrame with ac_no and ac_name."""
    year_dir = Path(data_dir) / f"raw/eci_{year}"
    records = []
    
    if not year_dir.exists():
        print(f"Warning: Directory {year_dir} not found.")
        return pd.DataFrame(columns=['ac_no', f'ac_name_{year}', f'ac_name_norm_{year}'])
        
    for file_path in year_dir.glob("*.jsonl"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                ac_no = record.get("ac_no")
                ac_name = record.get("ac_name")
                if ac_no is not None and ac_name is not None:
                    records.append({
                        'ac_no': ac_no,
                        f'ac_name_{year}': ac_name,
                        f'ac_name_norm_{year}': normalize_constituency_name(ac_name)
                    })
    
    return pd.DataFrame(records).sort_values('ac_no')

def run_fuzzy_match(data_dir: str, threshold: float = 90.0):
    """
    Matches ECI 2025 constituency names against ECI 2020 names using ac_no as key.
    Calculates fuzzy similarity score.
    Saves full results and mismatches.
    """
    df_2025 = load_eci_names(2025, data_dir)
    df_2020 = load_eci_names(2020, data_dir)
    
    if df_2025.empty or df_2020.empty:
        print("Error: Missing ECI data.")
        return
        
    # Join on ac_no
    df_joined = pd.merge(df_2025, df_2020, on='ac_no', how='outer')
    
    # Calculate similarity score
    def calculate_score(row):
        name1 = str(row.get('ac_name_norm_2025', ''))
        name2 = str(row.get('ac_name_norm_2020', ''))
        if not name1 or not name2:
            return 0.0
        return fuzz.token_sort_ratio(name1, name2)
        
    df_joined['similarity_score'] = df_joined.apply(calculate_score, axis=1)
    
    # Flag mismatches
    df_joined['is_match'] = df_joined['similarity_score'] >= threshold
    
    # Setup output dir
    out_dir = Path(data_dir) / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Save results
    full_out = out_dir / "fuzzy_match_results.csv"
    mismatches_out = out_dir / "fuzzy_match_mismatches.csv"
    
    df_joined.to_csv(full_out, index=False)
    
    mismatches = df_joined[~df_joined['is_match']]
    mismatches.to_csv(mismatches_out, index=False)
    
    print(f"Fuzzy match complete.")
    print(f"Total constituencies: {len(df_joined)}")
    print(f"Matches (score >= {threshold}): {len(df_joined) - len(mismatches)}")
    print(f"Mismatches: {len(mismatches)}")
    print(f"Results saved to {out_dir}")

if __name__ == "__main__":
    # Base dir: d:\BoothIQ\BoothIQ\data
    base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    run_fuzzy_match(base_data_dir)
