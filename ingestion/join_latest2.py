import os
import json
import glob
import pandas as pd
from pathlib import Path

def load_latest2_data(data_dir: str) -> pd.DataFrame:
    """
    Loads all latest2 indicator files for all constituencies,
    returning a single long-format DataFrame.
    """
    base_dir = Path(data_dir) / "raw/latest2"
    records = []
    
    if not base_dir.exists():
        print(f"Warning: Directory {base_dir} not found.")
        return pd.DataFrame()
        
    pattern = os.path.join(base_dir, "*.jsonl")
    files = glob.glob(pattern)
    
    print(f"Found {len(files)} files in raw/latest2 folder. Scanning and parsing...")
    
    for f_path in files:
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                for line in f:
                    record = json.loads(line.strip())
                    if not record:
                        continue
                    # Keep only database relevant fields
                    records.append({
                        'ac_no': int(record['ac_no']),
                        'dataset_type': str(record['dataset_type']),
                        'value': str(record['value']) if record.get('value') is not None else None,
                        'unit': str(record['unit']) if record.get('unit') is not None else None,
                        'last_updated': str(record['last_updated']) if record.get('last_updated') is not None else None
                    })
        except Exception as e:
            print(f"Error parsing file {f_path}: {e}")
            
    df = pd.DataFrame(records)
    print(f"Successfully processed {len(df)} indicator rows.")
    return df

if __name__ == "__main__":
    base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    df = load_latest2_data(base_data_dir)
    if not df.empty:
        print(f"Shape: {df.shape}")
        print(df.head())
