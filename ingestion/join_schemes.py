import json
import os
import pandas as pd
from pathlib import Path

def load_schemes_data(data_dir: str) -> pd.DataFrame:
    """
    Loads schemes JSONL files, flattens the nested structure, 
    and returns a DataFrame.
    """
    schemes_dir = Path(data_dir) / "raw/schemes"
    records = []
    
    if not schemes_dir.exists():
        print(f"Warning: Directory {schemes_dir} not found.")
        return pd.DataFrame()
        
    for file_path in schemes_dir.glob("*_schemes.jsonl"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                
                flat_record = {
                    'ac_no': record.get('ac_no'),
                    'district': record.get('district'),
                    'reporting_period': record.get('reporting_period'),
                    'scheme_data_is_district_estimate': record.get('scheme_data_is_district_estimate', False)
                }
                
                # MGNREGA
                mgnrega = record.get('mgnrega', {})
                flat_record.update({
                    'mgnrega_active_job_cards': mgnrega.get('active_job_cards_count'),
                    'mgnrega_expenditure_lakhs': mgnrega.get('total_expenditure_lakhs'),
                    'mgnrega_person_days': mgnrega.get('person_days_generated'),
                })
                
                # PMAY
                pmay = record.get('pmay', {})
                flat_record.update({
                    'pmay_homes_sanctioned': pmay.get('homes_sanctioned_count'),
                    'pmay_homes_completed': pmay.get('homes_completed_count'),
                    'pmay_allocated_funds_lakhs': pmay.get('allocated_funds_lakhs'),
                })
                
                # Ujjwala
                ujjwala = record.get('ujjwala', {})
                flat_record.update({
                    'ujjwala_gas_connections': ujjwala.get('gas_connections_count'),
                    'ujjwala_subsidy_disbursed_inr': ujjwala.get('subsidy_disbursed_inr'),
                })
                
                records.append(flat_record)
                
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values('ac_no')
    return df

if __name__ == "__main__":
    base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    df = load_schemes_data(base_data_dir)
    print(f"Loaded {len(df)} schemes records.")
