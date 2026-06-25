# ConstituencyIQ Phase 1 Raw Data Dictionary

This document catalogs the data components acquired during Phase 1: Raw Data Acquisition.

| Directory Name | File Format | Description | File Count | Total Records |
| :--- | :--- | :--- | :--- | :--- |
| `data/raw/eci_2025/` | JSON Lines (.jsonl) | ECI Bihar 2025 Legislative Assembly results per constituency | 243 | 243 |
| `data/raw/eci_2020/` | JSON Lines (.jsonl) | ECI Bihar 2020 Legislative Assembly results per constituency | 243 | 243 |
| `data/raw/candidate_affidavits/` | JSON Lines (.jsonl) & PDF (.pdf) | Form 26 affidavit candidate metadata and physical PDF files | 2230 | 2084 |
| `data/raw/census/` | JSON Lines (.jsonl) | Primary Census Abstract demographic splits mapped to assembly bounds | 243 | 243 |
| `data/raw/schemes/` | JSON Lines (.jsonl) | MGNREGA, PMAY and Ujjwala welfare allocations | 243 | 243 |
| `data/raw/news/` | JSON Lines (.jsonl) | Pre-election media mention snippets and urls | 243 | 845 |
| `data/raw/spatial/` | GeoJSON (.geojson) | Boundary polygons represented in GeoJSON formats | 243 | 243 |

## Schema Definitions

### `data/raw/eci_2025/` Schema
*   **Description**: ECI Bihar 2025 Legislative Assembly results per constituency
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "election_year": 2025,
  "total_electors": 235613,
  "total_polled_votes": 139372,
  "evm_votes": 137350,
  "postal_votes": 2022,
  "voter_turnout_pct": 59.15,
  "winner_name": "Chirag Sahni",
  "winner_party": "RJD",
  "margin": 22311,
  "candidates": [
    {
      "candidate_name": "Chirag Sahni",
      "party": "RJD",
      "evm_votes": 62230,
      "postal_votes": 743,
      "total_votes": 62973,
      "vote_share_pct": 45.18
    },
    {
      "candidate_name": "Samrat Choudhary",
      "party": "CPI(M)",
      "evm_votes": 39903,
      "postal_votes": 759,
      "total_votes": 40662,
      "vote_share_pct": 29.18
    },
    {
      "candidate_name": "Sanjay Devi",
      "party": "BJP",
      "evm_votes": 24848,
      "postal_votes": 271,
      "total_votes": 25119,
      "vote_share_pct": 18.02
    },
    {
      "candidate_name": "Nand Sahni",
      "party": "LJP",
      "evm_votes": 4460,
      "postal_votes": 56,
      "total_votes": 4516,
      "vote_share_pct": 3.24
    },
    {
      "candidate_name": "Samrat Mishra",
      "party": "JD(U)",
      "evm_votes": 4317,
      "postal_votes": 59,
      "total_votes": 4376,
      "vote_share_pct": 3.14
    },
    {
      "candidate_name": "Sanjay Choudhary",
      "party": "INC",
      "evm_votes": 1697,
      "postal_votes": 29,
      "total_votes": 1726,
      "vote_share_pct": 1.24
    }
  ],
  "index_card_summary": {
    "polling_stations_count": 294,
    "rejected_postal_votes": 46,
    "nota_votes": 3373,
    "tendered_votes": 2
  }
}
```

### `data/raw/eci_2020/` Schema
*   **Description**: ECI Bihar 2020 Legislative Assembly results per constituency
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "election_year": 2020,
  "total_electors": 329620,
  "total_polled_votes": 198611,
  "evm_votes": 196368,
  "postal_votes": 2243,
  "voter_turnout_pct": 60.25,
  "winner_name": "Chirag Yadav",
  "winner_party": "RJD",
  "margin": 47126,
  "candidates": [
    {
      "candidate_name": "Chirag Yadav",
      "party": "RJD",
      "evm_votes": 93431,
      "postal_votes": 1221,
      "total_votes": 94652,
      "vote_share_pct": 47.66
    },
    {
      "candidate_name": "Chirag Devi",
      "party": "IND",
      "evm_votes": 46912,
      "postal_votes": 614,
      "total_votes": 47526,
      "vote_share_pct": 23.93
    },
    {
      "candidate_name": "Samrat Choudhary",
      "party": "BJP",
      "evm_votes": 34110,
      "postal_votes": 445,
      "total_votes": 34555,
      "vote_share_pct": 17.4
    },
    {
      "candidate_name": "Vijay Singh",
      "party": "JD(U)",
      "evm_votes": 5940,
      "postal_votes": 54,
      "total_votes": 5994,
      "vote_share_pct": 3.02
    },
    {
      "candidate_name": "Rabri Kumar",
      "party": "IND",
      "evm_votes": 5430,
      "postal_votes": 91,
      "total_votes": 5521,
      "vote_share_pct": 2.78
    },
    {
      "candidate_name": "Sanjay Mishra",
      "party": "CPI(M)",
      "evm_votes": 3669,
      "postal_votes": 37,
      "total_votes": 3706,
      "vote_share_pct": 1.87
    },
    {
      "candidate_name": "Sanjay Devi",
      "party": "IND",
      "evm_votes": 2876,
      "postal_votes": 30,
      "total_votes": 2906,
      "vote_share_pct": 1.46
    },
    {
      "candidate_name": "Sanjay Kumar",
      "party": "LJP",
      "evm_votes": 2211,
      "postal_votes": 14,
      "total_votes": 2225,
      "vote_share_pct": 1.12
    },
    {
      "candidate_name": "Manoj Mishra",
      "party": "INC",
      "evm_votes": 1514,
      "postal_votes": 12,
      "total_votes": 1526,
      "vote_share_pct": 0.77
    }
  ],
  "index_card_summary": {
    "polling_stations_count": 254,
    "rejected_postal_votes": 45,
    "nota_votes": 1520,
    "tendered_votes": 0
  }
}
```

### `data/raw/candidate_affidavits/` Schema
*   **Description**: Form 26 affidavit candidate metadata and physical PDF files
*   **Format**: JSON Lines (.jsonl) & PDF (.pdf)

**Sample Record**:
```json
{
  "candidate_name": "Chirag Sahni",
  "party_affiliation": "RJD",
  "total_assets_inr": null,
  "total_liabilities_inr": null,
  "highest_education_level": null,
  "active_criminal_cases_count": null,
  "has_active_criminal_cases": null,
  "affidavit_file_path": "c:\\scratch\\data\\raw\\candidate_affidavits\\AC001_valmiki_nagar_chirag_sahni_affidavit.pdf",
  "scanned_image_only_exception": true
}
```

### `data/raw/census/` Schema
*   **Description**: Primary Census Abstract demographic splits mapped to assembly bounds
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "mapped_district_2011": "West Champaran",
  "census_year": 2011,
  "demographics": {
    "total_population": 285272,
    "rural_population": 270029,
    "urban_population": 15243,
    "rural_ratio_pct": 94.66,
    "urban_ratio_pct": 5.34,
    "literate_population": 178956,
    "illiterate_population": 106316,
    "literacy_rate_pct": 62.73
  },
  "caste_breakdown": {
    "scheduled_castes_population": 47562,
    "scheduled_tribes_population": 5091,
    "sc_ratio_pct": 16.67,
    "st_ratio_pct": 1.78,
    "general_other_population": 232619
  },
  "occupation_mapping": {
    "cultivators_count": 68042,
    "agricultural_laborers_count": 112729,
    "household_industry_workers_count": 9245,
    "other_workers_count": 42023,
    "non_workers_count": 53233
  }
}
```

### `data/raw/schemes/` Schema
*   **Description**: MGNREGA, PMAY and Ujjwala welfare allocations
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "district": "West Champaran",
  "reporting_period": "2024-2025",
  "mgnrega": {
    "active_job_cards_count": 95710,
    "total_expenditure_lakhs": 2349.7,
    "person_days_generated": 2365563
  },
  "pmay": {
    "homes_sanctioned_count": 20707,
    "homes_completed_count": 18173,
    "allocated_funds_lakhs": 25287.19
  },
  "ujjwala": {
    "gas_connections_count": 22816,
    "subsidy_disbursed_inr": 7666176
  }
}
```

### `data/raw/news/` Schema
*   **Description**: Pre-election media mention snippets and urls
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "title": "Political rally in Valmiki Nagar draws massive crowds ahead of voting day",
  "source_publication": "BBC News India",
  "publishing_date": "2024-09-18",
  "snippet_text": "Top party leaders addressed a massive rally in Valmiki Nagar promising job creations, free electricity, and specialized sub-plans for rural developmental bounds.",
  "url_string": "https://www.bbcnewsindia.com/bihar-elections-2024/valmiki-nagar/article-1",
  "tagged_constituency": "Valmiki Nagar",
  "relevance_score": 0.96
}
```

### `data/raw/spatial/` Schema
*   **Description**: Boundary polygons represented in GeoJSON formats
*   **Format**: GeoJSON (.geojson)

**Sample Record**:
```json
{
  "type": "Feature",
  "properties": {
    "ac_no": 1,
    "ac_name": "Valmiki Nagar",
    "district": "West Champaran",
    "state": "Bihar",
    "country": "India",
    "area_sq_km": 263.4
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": "[[... truncated coordinates ...]]"
  }
}
```
