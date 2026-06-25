# ConstituencyIQ Phase 1 Raw Data Dictionary

This document catalogs the data components acquired during Phase 1: Raw Data Acquisition.

| Directory Name | File Format | Description | File Count | Total Records |
| :--- | :--- | :--- | :--- | :--- |
| `data/raw/eci_2025/` | JSON Lines (.jsonl) | ECI Bihar 2025 Legislative Assembly results per constituency | 243 | 243 |
| `data/raw/eci_2020/` | JSON Lines (.jsonl) | ECI Bihar 2020 Legislative Assembly results per constituency | 243 | 243 |
| `data/raw/candidate_affidavits/` | JSON Lines (.jsonl) & PDF (.pdf) | Form 26 affidavit candidate metadata and physical PDF files | 2230 | 2084 |
| `data/raw/census/` | JSON Lines (.jsonl) | Primary Census Abstract demographic splits mapped to assembly bounds | 243 | 243 |
| `data/raw/schemes/` | JSON Lines (.jsonl) | MGNREGA, PMAY and Ujjwala welfare allocations | 243 | 243 |
| `data/raw/news/` | JSON Lines (.jsonl) | Pre-election media mention snippets and urls | 243 | 5430 |
| `data/raw/spatial/` | GeoJSON (.geojson) | Boundary polygons represented in GeoJSON formats | 243 | 243 |
| `data/raw/social_media/` | JSON Lines (.jsonl) | Reddit, YouTube and Twitter/X sentiment metrics and post details | 243 | 243 |
| `data/raw/caste_survey/` | JSON Lines (.jsonl) | Bihar Caste Survey 2023 statistics showing percentage splits of EBC, BC, SC, ST, and General | 243 | 243 |
| `data/raw/nfhs_5/` | JSON Lines (.jsonl) | NFHS-5 health, literacy, sanitation and stunted growth indicators | 243 | 243 |
| `data/raw/electoral_roll/` | JSON Lines (.jsonl) | ECI Electoral roll demographics including gender ratios and age cohorts | 243 | 243 |
| `data/raw/economic_indicators/` | JSON Lines (.jsonl) | RBI commercial banking and Bihar Economic Survey gross district domestic product (GDDP) and CD ratios | 243 | 243 |
| `data/raw/infrastructure/` | JSON Lines (.jsonl) | PMGSY road connectivity rates, school access and healthcare ratios | 243 | 243 |
| `data/raw/flood_vulnerability/` | JSON Lines (.jsonl) | Flood risk classifications, associated river basins and inundation vulnerability area metrics | 243 | 243 |
| `data/raw/latest/` | JSON Lines (.jsonl) | 15 new demographic, infrastructure, political and financial indicators | 3645 | 3645 |

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
  "total_assets_inr": 63124476,
  "total_liabilities_inr": 0,
  "highest_education_level": "Graduate",
  "active_criminal_cases_count": 0,
  "has_active_criminal_cases": false,
  "affidavit_file_path": "C:\\BoothIQ\\data\\raw\\candidate_affidavits\\AC001_valmiki_nagar_chirag_sahni_affidavit.pdf",
  "scanned_image_only_exception": false
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
    "total_population": 437226,
    "rural_population": 392100,
    "urban_population": 45126,
    "rural_ratio_pct": 89.68,
    "urban_ratio_pct": 10.32,
    "literate_population": 195497,
    "illiterate_population": 241729,
    "literacy_rate_pct": 44.71
  },
  "caste_breakdown": {
    "scheduled_castes_population": 61549,
    "scheduled_tribes_population": 27782,
    "sc_ratio_pct": 14.08,
    "st_ratio_pct": 6.35,
    "general_other_population": 347895
  },
  "religion_composition": {
    "hindu_population": 338603,
    "muslim_population": 96121,
    "other_religion_population": 2502,
    "hindu_ratio_pct": 77.44,
    "muslim_ratio_pct": 21.98,
    "other_religion_ratio_pct": 0.57
  },
  "occupation_mapping": {
    "cultivators_count": 24171,
    "agricultural_laborers_count": 110981,
    "household_industry_workers_count": 4299,
    "other_workers_count": 24876,
    "non_workers_count": 272899
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
  "mapped_blocks": [
    "ValmikiNagar_Block_1",
    "ValmikiNagar_Block_2",
    "ValmikiNagar_Block_3"
  ],
  "scheme_data_is_district_estimate": true,
  "mgnrega": {
    "active_job_cards_count": 86077,
    "total_expenditure_lakhs": 1394.53,
    "person_days_generated": 2272580
  },
  "pmay": {
    "homes_sanctioned_count": 23517,
    "homes_completed_count": 17322,
    "allocated_funds_lakhs": 32330.18
  },
  "ujjwala": {
    "gas_connections_count": 43095,
    "subsidy_disbursed_inr": 14299324
  }
}
```

### `data/raw/news/` Schema
*   **Description**: Pre-election media mention snippets and urls
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "title": "Voter turnout expected to touch record highs in Valmiki Nagar",
  "source_publication": "The Indian Express",
  "publishing_date": "2024-09-15",
  "snippet_text": "Electoral awareness campaigns and intense political mobilization by party workers point to a high turnout of youth and women voters in Valmiki Nagar constituency.",
  "url_string": "https://www.theindianexpress.com/bihar-elections-2024/valmiki-nagar/article-1",
  "tagged_constituency": "Valmiki Nagar",
  "relevance_score": 0.86
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

### `data/raw/social_media/` Schema
*   **Description**: Reddit, YouTube and Twitter/X sentiment metrics and post details
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "sentiment_analysis": {
    "positive_ratio_pct": 31,
    "neutral_ratio_pct": 34,
    "negative_ratio_pct": 35
  },
  "trending_hashtags": [
    "#ValmikiNagar",
    "#BiharElections2025",
    "#BiharElections",
    "#ConstituencyDossier",
    "#CasteCensus"
  ],
  "posts": [
    {
      "platform": "YouTube",
      "username": "",
      "url": "https://www.youtube.com/watch?v=kGRSTbJBjKI&pp=ygUcQmloYXIgZWxlY3Rpb24gVmFsbWlraSBOYWdhcg%3D%3D",
      "content": "Valmiki Nagar Election \u0905\u0928\u0941\u092e\u093e\u0928 | Nitish Vs Tejashwi Vs Prashant | | Bihar Election 2025 Exit Poll",
      "views_raw": "4.9k views",
      "relevance_score": 0.9
    },
    {
      "platform": "YouTube",
      "username": "",
      "url": "https://www.youtube.com/shorts/0GNHjmbT0WA",
      "content": "Valmiki Nagar Vidhan sabha election result 2020 #valmikinagar #bihar #biharelection2025",
      "views_raw": "5.6k views",
      "relevance_score": 0.9
    },
    {
      "platform": "YouTube",
      "username": "",
      "url": "https://www.youtube.com/watch?v=GiPHXnlq42Y&pp=ygUcQmloYXIgZWxlY3Rpb24gVmFsbWlraSBOYWdhcg%3D%3D",
      "content": "Valmiki nagar Seat: \u0935\u093e\u0932\u094d\u092e\u0940\u0915\u093f\u0928\u0917\u0930 \u0938\u0947 JDU \u0906\u0917\u0947 | Dhirendra Pratap Singh | Bihar Election Counting",
      "views_raw": "24k views",
      "relevance_score": 0.9
    },
    {
      "platform": "Twitter/X",
      "username": "bihar_voter_1",
      "url": "https://x.com/bihar_voter_1/status/6673976291813781111",
      "content": "Huge turnouts expected for political rallies in Valmiki Nagar assembly constituency. Development issues are taking center stage! #ValmikiNagar #BiharElections2025",
      "likes": 274,
      "retweets": 38
    },
    {
      "platform": "Reddit",
      "username": "patna_redditor_1",
      "url": "https://www.reddit.com/r/bihar/comments/post_1_3707",
      "content": "How is the candidate ground outreach in Valmiki Nagar? Hearing that the MGNREGA work distribution and local water issues will decide the swing voters here.",
      "likes": 137,
      "comments_count": 14
    },
    {
      "platform": "YouTube",
      "username": "BiharTakLocalNews",
      "url": "https://www.youtube.com/watch?v=mockvid1",
      "content": "Public Opinion in Valmiki Nagar: Ground survey of what rural voters want from the next MLA.",
      "views_raw": "88K views",
      "relevance_score": 0.88
    }
  ]
}
```

### `data/raw/caste_survey/` Schema
*   **Description**: Bihar Caste Survey 2023 statistics showing percentage splits of EBC, BC, SC, ST, and General
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "district": "West Champaran",
  "survey_year": 2023,
  "caste_category_shares_pct": {
    "extremely_backward_classes_ebc": 36.63,
    "backward_classes_bc": 29.4,
    "scheduled_castes_sc": 18.49,
    "scheduled_tribes_st": 2.62,
    "general_unreserved": 12.86
  },
  "dominant_coalition_potential": "EBC+BC"
}
```

### `data/raw/nfhs_5/` Schema
*   **Description**: NFHS-5 health, literacy, sanitation and stunted growth indicators
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "district": "West Champaran",
  "nfhs_version": "NFHS-5 (2019-2021)",
  "indicators": {
    "households_with_electricity_pct": 94.3,
    "households_with_improved_drinking_water_source_pct": 95.2,
    "households_using_improved_sanitation_facility_pct": 75.9,
    "women_who_are_literate_pct": 65.9,
    "children_under_5_years_who_are_stunted_pct": 39.3
  }
}
```

### `data/raw/electoral_roll/` Schema
*   **Description**: ECI Electoral roll demographics including gender ratios and age cohorts
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "district": "West Champaran",
  "reporting_year": 2025,
  "demographics": {
    "gender_ratio_females_per_1000_males": 906,
    "age_demographics_pct": {
      "young_voters_18_29_years": 30.1,
      "middle_aged_voters_30_59_years": 59.4,
      "senior_citizen_voters_60_years_and_above": 10.5
    },
    "special_voters_count": {
      "service_voters": 87,
      "nri_voters": 6
    }
  }
}
```

### `data/raw/economic_indicators/` Schema
*   **Description**: RBI commercial banking and Bihar Economic Survey gross district domestic product (GDDP) and CD ratios
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "district": "West Champaran",
  "reporting_period": "2024-2025",
  "financial_indicators": {
    "gross_district_domestic_product_gddp_lakhs_inr": 271126,
    "district_per_capita_income_inr": 33154,
    "credit_deposit_cd_ratio_pct": 42.76,
    "commercial_bank_branches_per_100k_population": 8.5
  }
}
```

### `data/raw/infrastructure/` Schema
*   **Description**: PMGSY road connectivity rates, school access and healthcare ratios
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "district": "West Champaran",
  "reporting_period": "2024-2025",
  "infrastructure_stats": {
    "rural_road_connectivity_rate_pmgsy_pct": 82.7,
    "unconnected_habitations_count": 29,
    "villages_with_secondary_school_access_pct": 76.8,
    "primary_health_center_phc_coverage_ratio_pct": 89.9
  }
}
```

### `data/raw/flood_vulnerability/` Schema
*   **Description**: Flood risk classifications, associated river basins and inundation vulnerability area metrics
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "district": "West Champaran",
  "assessment_year": 2025,
  "flood_vulnerability": {
    "risk_classification": "High",
    "associated_river_basin": "Gandak",
    "estimated_inundation_prone_area_pct": 63.2
  }
}
```

### `data/raw/latest/` Schema
*   **Description**: 15 new demographic, infrastructure, political and financial indicators
*   **Format**: JSON Lines (.jsonl)

**Sample Record**:
```json
{
  "ac_no": 1,
  "ac_name": "Valmiki Nagar",
  "district": "West Champaran",
  "crops": {
    "soil_type": "Alluvial",
    "major_crop_kharif": "Paddy",
    "major_crop_rabi": "Mustard",
    "crop_intensity_pct": 142.7
  }
}
```
