import json
import os
import pandas as pd
from pathlib import Path

def load_nfhs_data(data_dir: str) -> pd.DataFrame:
    """
    Loads NFHS-5 JSONL files, flattens the nested indicators,
    and returns a DataFrame.
    """
    nfhs_dir = Path(data_dir) / "raw/nfhs_5"
    records = []
    
    if not nfhs_dir.exists():
        print(f"Warning: Directory {nfhs_dir} not found.")
        return pd.DataFrame()
        
    for file_path in nfhs_dir.glob("*_nfhs5.jsonl"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                
                flat_record = {
                    'ac_no': record.get('ac_no'),
                    'nfhs_version': record.get('nfhs_version', 'NFHS-5 (2019-2021)'),
                }
                
                # Indicators
                indicators = record.get('indicators', {})
                flat_record.update({
                    'households_with_electricity_pct': indicators.get('households_with_electricity_pct'),
                    'households_with_improved_drinking_water_source_pct': indicators.get('households_with_improved_drinking_water_source_pct'),
                    'households_using_improved_sanitation_facility_pct': indicators.get('households_using_improved_sanitation_facility_pct'),
                    'women_who_are_literate_pct': indicators.get('women_who_are_literate_pct'),
                    'children_under_5_years_who_are_stunted_pct': indicators.get('children_under_5_years_who_are_stunted_pct'),
                })
                
                records.append(flat_record)
                
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values('ac_no')
    return df

if __name__ == "__main__":
    base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    df = load_nfhs_data(base_data_dir)
    print(f"Loaded {len(df)} NFHS-5 records.")
