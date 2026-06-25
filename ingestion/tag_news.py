import json
import os
import pandas as pd
from pathlib import Path
from normalize import normalize_constituency_name
from fuzzy_match import load_eci_names

def process_news_data(data_dir: str) -> pd.DataFrame:
    """
    Loads news JSONL files, extracts articles, and maps them to ac_no
    using the ECI 2025 canonical constituency list.
    """
    # Load canonical mapping from 2025 ECI data
    df_master = load_eci_names(2025, data_dir)
    # create mapping: normalized_name -> ac_no
    name_to_ac = dict(zip(df_master['ac_name_norm_2025'], df_master['ac_no']))
    
    news_dir = Path(data_dir) / "raw/news"
    records = []
    
    if not news_dir.exists():
        print(f"Warning: Directory {news_dir} not found.")
        return pd.DataFrame()
        
    for file_path in news_dir.glob("*_news.jsonl"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                tagged_name = record.get('tagged_constituency', '')
                norm_tagged_name = normalize_constituency_name(tagged_name)
                
                ac_no = name_to_ac.get(norm_tagged_name)
                
                # If not matched, leave ac_no as None (unassigned)
                records.append({
                    'ac_no': ac_no,
                    'title': record.get('title'),
                    'source_publication': record.get('source_publication'),
                    'publishing_date': record.get('publishing_date'),
                    'snippet_text': record.get('snippet_text'),
                    'url_string': record.get('url_string'),
                    'tagged_constituency': tagged_name,
                    'relevance_score': record.get('relevance_score'),
                })
                
    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    df = process_news_data(base_data_dir)
    print(f"Loaded {len(df)} news articles.")
    print(f"Unassigned articles: {df['ac_no'].isna().sum()}")
