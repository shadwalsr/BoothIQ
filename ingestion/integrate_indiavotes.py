import json
import glob
import os

# Paths
raw_dir_2020 = 'd:/BoothIQ/BoothIQ/data/raw/eci_2020'
raw_dir_2025 = 'd:/BoothIQ/BoothIQ/data/raw/eci_2025'
processed_file_2020 = 'd:/BoothIQ/BoothIQ/data/processed/eci_results_2020.jsonl'
processed_file_2025 = 'd:/BoothIQ/BoothIQ/data/processed/eci_results_2025.jsonl'
iv_file = 'd:/BoothIQ/BoothIQ/scratch/indiavotes_results_2020.json'
map_file = 'd:/BoothIQ/BoothIQ/scratch/indiavotes_to_eci_map.json'

# Load mapping and IndiaVotes data
with open(map_file, 'r') as f:
    mapping = json.load(f)
with open(iv_file, 'r') as f:
    iv_data = json.load(f)
    
# Create reverse mapping: ECI name -> IndiaVotes data
eci_to_iv = {}
for iv_name, eci_name in mapping.items():
    if iv_name in iv_data:
        eci_to_iv[eci_name] = iv_data[iv_name]
        
def process_year(raw_dir, processed_file, is_2025=False):
    processed_records = []
    
    # Process each raw JSONL file
    for filename in glob.glob(os.path.join(raw_dir, '*.jsonl')):
        with open(filename, 'r') as f:
            for line in f:
                record = json.loads(line)
                ac_name_lower = record['ac_name'].lower().replace('-', ' ').strip()
                
                # If we have real data for this constituency
                if ac_name_lower in eci_to_iv:
                    real_data = eci_to_iv[ac_name_lower]
                    
                    # Update all winner fields to prevent mismatches
                    record['winner'] = real_data['candidate']
                    record['winner_name'] = real_data['candidate']
                    
                    # Fix party mapping inconsistencies (e.g. CPI(ML) (L) -> CPI(ML)(L))
                    party = real_data['party'].replace(' ', '')
                    record['party'] = party
                    record['winner_party'] = party
                    
                    # Make sure the top candidate in the candidates list matches
                    if len(record.get('candidates', [])) > 0:
                         record['candidates'][0]['candidate_name'] = real_data['candidate']
                         record['candidates'][0]['party'] = party
                    
                    # Mark as NOT simulated anymore
                    record['is_simulated'] = False
                
                processed_records.append(record)
                
    # Sort by AC No
    processed_records.sort(key=lambda x: x['ac_no'])
    
    # Write to processed file
    os.makedirs(os.path.dirname(processed_file), exist_ok=True)
    with open(processed_file, 'w') as f:
        for record in processed_records:
            f.write(json.dumps(record) + '\n')
            
    print(f'Wrote {len(processed_records)} records to {processed_file}')

# Process both years
process_year(raw_dir_2020, processed_file_2020)
process_year(raw_dir_2025, processed_file_2025, is_2025=True)
