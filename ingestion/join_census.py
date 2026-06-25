import json
import os
import pandas as pd
from pathlib import Path

def load_census_data(data_dir: str) -> pd.DataFrame:
    """
    Loads census JSONL files, flattens the nested structure, 
    and returns a DataFrame.
    """
    census_dir = Path(data_dir) / "raw/census"
    records = []
    
    if not census_dir.exists():
        print(f"Warning: Directory {census_dir} not found.")
        return pd.DataFrame()
        
    for file_path in census_dir.glob("*_census.jsonl"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                
                flat_record = {
                    'ac_no': record.get('ac_no'),
                    'mapped_district_2011': record.get('mapped_district_2011'),
                    'census_year': record.get('census_year', 2011),
                }
                
                # Demographics
                demo = record.get('demographics', {})
                flat_record.update({
                    'total_population': demo.get('total_population'),
                    'rural_population': demo.get('rural_population'),
                    'urban_population': demo.get('urban_population'),
                    'rural_ratio_pct': demo.get('rural_ratio_pct'),
                    'urban_ratio_pct': demo.get('urban_ratio_pct'),
                    'literate_population': demo.get('literate_population'),
                    'illiterate_population': demo.get('illiterate_population'),
                    'literacy_rate_pct': demo.get('literacy_rate_pct'),
                })
                
                # Caste
                caste = record.get('caste_breakdown', {})
                flat_record.update({
                    'sc_population': caste.get('scheduled_castes_population'),
                    'st_population': caste.get('scheduled_tribes_population'),
                    'sc_ratio_pct': caste.get('sc_ratio_pct'),
                    'st_ratio_pct': caste.get('st_ratio_pct'),
                    'general_other_population': caste.get('general_other_population'),
                })
                
                # Religion
                religion = record.get('religion_composition', {})
                flat_record.update({
                    'hindu_population': religion.get('hindu_population'),
                    'muslim_population': religion.get('muslim_population'),
                    'other_religion_population': religion.get('other_religion_population'),
                    'hindu_ratio_pct': religion.get('hindu_ratio_pct'),
                    'muslim_ratio_pct': religion.get('muslim_ratio_pct'),
                    'other_religion_ratio_pct': religion.get('other_religion_ratio_pct'),
                })
                
                # Occupation
                occ = record.get('occupation_mapping', {})
                flat_record.update({
                    'cultivators_count': occ.get('cultivators_count'),
                    'agricultural_laborers_count': occ.get('agricultural_laborers_count'),
                    'household_industry_workers_count': occ.get('household_industry_workers_count'),
                    'other_workers_count': occ.get('other_workers_count'),
                    'non_workers_count': occ.get('non_workers_count'),
                })
                
                records.append(flat_record)
                
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values('ac_no')
    return df

if __name__ == "__main__":
    base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    df = load_census_data(base_data_dir)
    print(f"Loaded {len(df)} census records.")
