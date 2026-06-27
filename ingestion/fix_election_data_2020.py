"""
Fix 2020 election data: Replace synthetic/fabricated 2020 Bihar election results 
with real winner data parsed from Wikipedia.
"""

import os
import json
import sys
from pathlib import Path

def standardize_party(party: str) -> str:
    mapping = {
        "BJP": "BJP",
        "JD(U)": "JD(U)",
        "RJD": "RJD",
        "INC": "INC",
        "CPI(ML)": "CPI(ML)(L)",
        "AIMIM": "AIMIM",
        "VIP": "VIP",
        "HAM": "HAM(S)",
        "CPI(M)": "CPI(M)",
        "CPI": "CPI",
        "LJP": "LJP",
        "BSP": "BSP",
        "IND": "IND"
    }
    return mapping.get(party, party)

def update_jsonl_files(ac_winner_map: dict, data_dir: str):
    raw_dir = os.path.join(data_dir, "data", "raw", "eci_2020")
    if not os.path.isdir(raw_dir):
        print(f"ERROR: Raw dir not found: {raw_dir}")
        return
    
    updated = 0
    for fname in sorted(os.listdir(raw_dir)):
        if not fname.endswith('.jsonl'):
            continue
        filepath = os.path.join(raw_dir, fname)
        records = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                records.append(json.loads(line))
        
        modified = False
        for rec in records:
            ac_no = rec.get('ac_no')
            # Since ac_no is integer, convert key to int
            ac_key = int(ac_no)
            if ac_key in ac_winner_map:
                real = ac_winner_map[ac_key]
                old_winner = rec.get('winner_name', '')
                rec['winner_name'] = real['winner_name']
                rec['winner_party'] = real['winner_party']
                
                # Also update candidates list if present
                if 'candidates' in rec and isinstance(rec['candidates'], list):
                    for cand in rec['candidates']:
                        if cand.get('candidate_name') == old_winner:
                            cand['candidate_name'] = real['winner_name']
                            cand['party'] = real['winner_party']
                            break
                    
                    found = False
                    for i, cand in enumerate(rec['candidates']):
                        if cand.get('candidate_name') == real['winner_name']:
                            found = True
                            if i > 0:
                                rec['candidates'].insert(0, rec['candidates'].pop(i))
                            break
                    if not found and rec['candidates']:
                        rec['candidates'][0]['candidate_name'] = real['winner_name']
                        rec['candidates'][0]['party'] = real['winner_party']
                
                modified = True
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                for rec in records:
                    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            updated += 1
    
    print(f"Updated {updated} 2020 JSONL files.")

def update_supabase(ac_winner_map: dict):
    from dotenv import load_dotenv
    load_dotenv()
    from load_supabase import get_supabase_client
    
    supabase = get_supabase_client()
    
    updated = 0
    errors = 0
    for ac_no, data in sorted(ac_winner_map.items()):
        try:
            resp = supabase.table("election_results_2020").update({
                "winner_name": data["winner_name"],
                "winner_party": data["winner_party"],
            }).eq("ac_no", ac_no).execute()
            updated += 1
        except Exception as e:
            print(f"  ERROR updating AC {ac_no}: {e}")
            errors += 1
    
    print(f"Supabase 2020: {updated} updated, {errors} errors.")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Load parsed JSON
    json_path = os.path.join(
        r"C:\Users\shadw\.gemini\antigravity\brain\b7e8b8b0-1e53-4e39-8681-ffecad6312ba",
        "scratch", "results_2020.json"
    )
    
    with open(json_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
        
    ac_winner_map = {}
    for ac_str, val in parsed_data.items():
        ac_no = int(ac_str)
        ac_winner_map[ac_no] = {
            "winner_name": val["winner_name"],
            "winner_party": standardize_party(val["winner_party"])
        }
        
    print("=" * 60)
    print("STEP 1: Updating 2020 raw JSONL files...")
    print("=" * 60)
    update_jsonl_files(ac_winner_map, base_dir)
    
    print("\n" + "=" * 60)
    print("STEP 2: Updating Supabase 2020 table...")
    print("=" * 60)
    update_supabase(ac_winner_map)
    
    print("\nDone! 2020 Election data has been corrected.")

if __name__ == "__main__":
    main()
