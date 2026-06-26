# ConstituencyIQ Case Study

## 1. Problem Statement
Political campaigns in Bihar face a massive data fragmentation challenge. While rich data exists—ranging from ECI historical polling figures and NFHS-5 health indicators to real-time social media sentiment and district-level economic data—it is siloed across dozens of formats and varying levels of geographic granularity. Decision-makers lack a unified, hyper-local intelligence layer that can seamlessly merge demographic baselines with real-time news discourse to produce actionable campaign strategies at the assembly constituency (AC) level.

## 2. Methodology
ConstituencyIQ solves this by building an automated ingestion and synthesis pipeline:
- **Data Acquisition**: We collected raw data across 15+ dimensions including 2020 & 2025 ECI results, 2011 Census demographic estimates, MGNREGA/PMAY welfare allocations, and real-time news/social media sentiment.
- **Geospatial Mapping**: District and block-level data (like NFHS-5 and economic indicators) were mapped down to the 243 Bihar Assembly Constituencies using proportional area weighting and GeoJSON boundary intersections.
- **Unified Schema**: All disparate datasets were flattened into a single, cohesive JSON Lines format and loaded into a Supabase PostgreSQL database.

## 3. Feature Engineering Rationale
To make the data actionable, raw metrics were transformed into analytical features:
- **Welfare Penetration Index**: Combined MGNREGA, PMAY, and Ujjwala beneficiary counts relative to the total eligible population to gauge incumbent advantage.
- **Vulnerability Scores**: Mapped historical flood data to constituency polygons to create a "Flood Risk Index," which historically correlates with anti-incumbency in specific northern Bihar ACs.
- **Caste Calculus**: Interpolated the 2023 Bihar Caste Survey data down to the AC level to estimate EBC, BC, SC, and General category voting blocs, a critical necessity in Bihar electoral math.

## 4. NLP Approach (News & Sentiment)
Understanding the local discourse required processing unstructured data:
- **Entity Resolution**: We utilized fuzzy matching (Levenshtein distance) to correctly map varying English/Hindi spellings of candidate names and constituencies from news APIs.
- **Sentiment Scoring**: Applied NLP sentiment analysis models to pre-election media snippets and social media posts (Twitter/X, Reddit, YouTube) to generate an aggregated `sentiment_score` (-1 to 1) for each constituency.
- **Discourse Tagging**: Extracted key topics (e.g., "unemployment", "infrastructure", "law and order") to identify the dominant narrative driving the conversation in each AC.

## 5. Clustering & Validation
To simplify strategic planning, we applied unsupervised machine learning (K-Means Clustering) to group the 243 constituencies into distinct "Personas".
- **Algorithm**: Used K-Means with Silhouette Analysis to determine the optimal number of clusters based on demographic, economic, and political features.
- **Personas Generated**: 
  1. *Urban Economic Hubs* (High literacy, high commercial banking, pro-incumbency bias)
  2. *Agrarian Heartland* (High welfare dependency, high flood risk, caste-driven voting)
  3. *Developing Periphery* (Low infrastructure, high migration, anti-incumbency sentiment)
- **Validation**: We validated the clusters by cross-referencing them with historical 2020 election margins and found strong correlations between the generated personas and the eventual winning party alignments.

## 6. Example Dossier Walkthrough
The core output of ConstituencyIQ is the **Constituency Dossier**:
1. **Header**: Displays the constituency name, current MLA, and the assigned Cluster Persona (e.g., "Agrarian Heartland").
2. **Electoral Math**: Shows the 2020 vs 2025 margin shifts, voter turnout, and candidate vote shares.
3. **Demographic Snapshot**: Visualizes the caste split (EBC, SC, etc.) alongside NFHS-5 health indicators.
4. **Discourse & Sentiment**: Highlights the current media sentiment score and trending local issues.
5. **Export**: The entire view can be exported to a clean, offline-readable PDF for field workers.

## 7. Limitations & Future Work
- **Data Latency**: The 2011 Census is severely outdated; mapping it to 2025 realities introduces a margin of error.
- **Granularity Mismatches**: District-level economic and health (NFHS) data mapped uniformly across underlying constituencies masks intra-district inequality.
- **Future Enhancements**: We plan to integrate real-time booth-level polling data and deploy predictive models for voter turnout estimation.
