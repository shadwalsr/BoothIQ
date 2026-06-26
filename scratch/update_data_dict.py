
import re

metadata = {
    "eci_2025": {"source": "Election Commission of India (ECI)", "date": "2025", "granularity": "Constituency (AC)", "limitations": "Provisional results until certified. Post-election data."},
    "eci_2020": {"source": "Election Commission of India (ECI)", "date": "2020", "granularity": "Constituency (AC)", "limitations": "Historical data, boundaries fixed but demographic compositions shift."},
    "candidate_affidavits": {"source": "ECI Form 26 Affidavits", "date": "2025", "granularity": "Candidate Level", "limitations": "Self-reported data; potential underreporting of assets or criminal cases."},
    "census": {"source": "Census of India", "date": "2011", "granularity": "Constituency (Mapped from District/Tehsil)", "limitations": "Severely outdated (2011). Estimates mapped to AC boundaries may contain geospatial aggregation errors."},
    "schemes": {"source": "Ministry of Rural Development / MoPNG", "date": "2023-2024", "granularity": "Constituency (Mapped from District)", "limitations": "Beneficiary counts mapped from district level. Leakage or duplication in registries possible."},
    "news": {"source": "News API / Media Scraping", "date": "2025", "granularity": "Constituency Level Mentions", "limitations": "Urban bias in coverage; rural constituencies underrepresented in digital media."},
    "spatial": {"source": "DataMeet / ECI GIS", "date": "2020", "granularity": "Constituency Polygons", "limitations": "Minor boundary inaccuracies compared to official but unpublished topographies."},
    "social_media": {"source": "Reddit, YouTube, Twitter/X APIs", "date": "2025", "granularity": "Constituency/Candidate Level", "limitations": "Bot activity and non-voter sentiment can skew metrics. Highly urban-biased."},
    "caste_survey": {"source": "Bihar Caste-based Survey", "date": "2023", "granularity": "District / Constituency Approximations", "limitations": "Extrapolated to AC boundaries. Survey methodology faced political scrutiny."},
    "nfhs_5": {"source": "National Family Health Survey-5", "date": "2019-2021", "granularity": "District Level", "limitations": "District-level averages applied uniformly to underlying constituencies. Masks intra-district variance."},
    "electoral_roll": {"source": "Chief Electoral Officer, Bihar", "date": "2025", "granularity": "Constituency / Booth Level", "limitations": "Subject to periodic revision. Dead voters or duplicates might inflate numbers."},
    "economic_indicators": {"source": "RBI / Bihar Economic Survey", "date": "2023-2024", "granularity": "District Level", "limitations": "Macro indicators (GDDP, CD Ratio) mapped to ACs. Fails to capture hyper-local economic hubs."},
    "infrastructure": {"source": "PMGSY / Ministry of Health", "date": "2023-2024", "granularity": "Block / Constituency", "limitations": "Official targets often overstate actual physical completion. Maintenance quality not captured."},
    "flood_vulnerability": {"source": "Bihar Disaster Management Dept", "date": "2023", "granularity": "Constituency / River Basin", "limitations": "Annual variability not fully modeled; relies on historical inundation zones."},
    "latest": {"source": "Aggregated APIs", "date": "2025", "granularity": "Constituency", "limitations": "Rapidly changing data. Occasional API lag or downtime."},
    "latest1": {"source": "Aggregated APIs", "date": "2025", "granularity": "Constituency", "limitations": "Extended indicators. High sparsity in certain rural ACs."},
    "latest2": {"source": "Aggregated APIs", "date": "2025", "granularity": "Constituency", "limitations": "Supplementary data. Subject to imputation for missing values."},
    "latest3": {"source": "Aggregated APIs", "date": "2025", "granularity": "Constituency", "limitations": "Deep demographic splits. Margin of error increases with granularity."}
}

with open("c:/BoothIQ/docs/data_dictionary.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
current_schema = None

for line in lines:
    new_lines.append(line)
    
    match = re.match(r"^### `data/raw/([^/]+)/` Schema", line)
    if match:
        current_schema = match.group(1)
        
    if current_schema and line.startswith("*   **Format**:"):
        meta = metadata.get(current_schema, {})
        if meta:
            new_lines.append(f"*   **Source**: {meta.get('source', 'Unknown')}\n")
            new_lines.append(f"*   **Date**: {meta.get('date', 'Unknown')}\n")
            new_lines.append(f"*   **Granularity**: {meta.get('granularity', 'Unknown')}\n")
            new_lines.append(f"*   **Limitations**: {meta.get('limitations', 'None')}\n")
        current_schema = None

with open("c:/BoothIQ/docs/data_dictionary.md", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Updated data_dictionary.md")

