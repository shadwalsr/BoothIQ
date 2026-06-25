# Build Procedure: ConstituencyIQ (Constituency Intelligence Dossier)

This is the step-by-step execution plan for the PRD. Each phase has a clear exit condition — don't move to the next phase until the exit condition is met, or you'll be debugging two layers of problems at once later.

---

## Phase 0: Environment & Scope Lock (Day 1-2)

**Step 1.** Lock the scope for v1: state = Bihar, elections = 2025 (current) vs 2020 (prior), constituency count = 243. Write this down somewhere visible — every time you're tempted to add a second state or booth-level data, you're scope-creeping.

**Step 2.** Set up the repo structure:
```
constituencyiq/
  ingestion/        # scripts to pull and clean raw data
  pipeline/          # feature engineering, clustering, NLP
  backend/           # FastAPI app
  frontend/           # React + TS app
  data/raw/          # untouched downloaded files
  data/processed/    # cleaned, joined tables
  docs/              # writeup, data dictionary
```

**Step 3.** Provision Supabase project, get connection string, confirm you can read/write a test table from Python and from the FastAPI app.

**Step 4.** Set up a `data_dictionary.md` file in `docs/` immediately. Every field you add later gets one line here: source, date, granularity, confidence. You will forget where a number came from within two weeks otherwise — write it down as you go, not at the end.

**Exit condition:** Repo scaffolded, Supabase reachable, data dictionary file exists (even empty).

---

## Phase 1: Raw Data Acquisition (Week 1)

Do this in order — each step unblocks the next.

**Step 1. ECI results (2025 and 2020).**
- Download booth/constituency-wise results from results.eci.gov.in for Bihar 2025.
- Download the equivalent for Bihar 2020.
- Save raw, untouched files to `data/raw/eci_2025/` and `data/raw/eci_2020/`.
- Open both and note column names, naming conventions for constituencies — write any inconsistency you spot into the data dictionary now.

**Step 2. Census 2011 demographics.**
- Pull district/block-level Census tables (literacy, religion, SC/ST, occupation, urban/rural) from censusindia.gov.in or census2011.co.in.
- Save raw files to `data/raw/census/`.
- Find or build a district-to-constituency mapping table — this is the single most tedious manual step in the whole project. Budget a full day. Cross-reference against the ECI constituency list.

**Step 3. Welfare scheme data.**
- Pull MGNREGA beneficiary counts (nrega.nic.in, Bihar state page) at whatever granularity is available (likely block-level).
- Pull PMAY and Ujjwala beneficiary stats from their respective dashboards.
- Save to `data/raw/schemes/`.
- Note in the data dictionary which schemes are constituency-level vs district/block-level — this determines your confidence flag later.

**Step 4. News/discourse data.**
- Set up a NewsAPI free-tier account (or equivalent) and write a basic script to pull articles mentioning Bihar + each constituency name for the pre-election window (roughly Sept–Nov 2024 for the 2025 election).
- Supplement manually for high-profile constituencies if API coverage is thin (search Indian Express Bihar, Hindustan Times Bihar directly).
- Save raw article text + metadata (date, source, constituency tag) to `data/raw/news/`.
- Expect uneven coverage — rural/smaller seats will have very little. Don't try to fix this now, just note it.

**Exit condition:** All four raw data buckets exist on disk, each with at least a rough constituency or district key you can join on later.

---

## Phase 2: Cleaning & Joining (Week 2)

**Step 1.** Write a normalization function for constituency names (lowercase, strip whitespace, remove punctuation) and apply it to every dataset's constituency/district column.

**Step 2.** Fuzzy-match ECI 2025 constituency names against ECI 2020 names using `fuzzywuzzy` or `rapidfuzz`. Anything below a similarity threshold (e.g. 90%) gets manually resolved — open a spreadsheet, eyeball the mismatches, fix by hand. This list is usually short (delimitation changes, minor spelling differences).

**Step 3.** Join Census district/block data onto the constituency master table using your mapping from Phase 1 Step 2. Where a constituency spans multiple Census blocks, aggregate (population-weighted average for rates, sum for counts).

**Step 4.** Join scheme data the same way. Flag every row where the join was at district level rather than true constituency level — add a boolean column like `scheme_data_is_district_estimate`.

**Step 5.** Tag each news article to a constituency (string match on constituency name or known local landmarks/town names within it). Articles that don't match anything get dropped or bucketed as "state-level, unassigned."

**Step 6.** Write all joined tables into Supabase using the schema from the PRD (constituencies, election_results_2025, election_results_2020, turnout, schemes, news_articles).

**Step 7.** Run a basic completeness check: what % of constituencies have a Census match, a scheme match, at least one news article. Log this — it directly informs your confidence flags later and your AC2 acceptance criterion (95% core-section completeness).

**Exit condition:** Every constituency has a row in the master table with at minimum electoral + demographic data populated; gaps are logged, not silently dropped.

---

## Phase 3: Feature Engineering (Week 3, first half)

**Step 1.** Compute electoral features per constituency: turnout delta, vote share swing, margin %, competitiveness score, anti-incumbency magnitude. Write this as a single Python function that takes the joined table and returns a new features dataframe — keep it reusable, you'll rerun it as data gets corrected.

**Step 2.** Compute demographic ratios: literacy normalized, urbanization %, SC/ST %, agriculture dependency %, religion composition vector.

**Step 3.** Compute the scheme penetration score (weighted combination of MGNREGA/PMAY/Ujjwala beneficiary % — start with equal weights, you can tune later).

**Step 4.** Run EDA: correlation heatmap across all features, scatter plots of the pairs you expect to be related (turnout vs literacy, swing vs scheme penetration). This is where you catch data errors — if something correlates the opposite direction of what's politically sane, go back and check the join, not the math.

**Step 5.** Write the features table back to Supabase (`constituency_features`).

**Exit condition:** Every constituency has a populated features row; EDA plots reviewed and any obvious data anomalies investigated and resolved.

---

## Phase 4: NLP Discourse Layer (Week 3, second half)

**Step 1.** Load all tagged news articles, generate sentence embeddings (`all-MiniLM-L6-v2` via sentence-transformers — fast, good enough for this).

**Step 2.** Run BERTopic on the embeddings to get topic clusters. Inspect the top words per topic.

**Step 3.** Manually map each auto-generated topic to your fixed taxonomy (inflation, communal, development, welfare, caste, unemployment, other). This is a judgment call — write down your mapping rationale in the data dictionary so it's defensible later.

**Step 4.** Aggregate topic frequency per constituency to get a discourse vector (% of articles per topic).

**Step 5.** For constituencies with fewer than a defined threshold of articles (e.g. <3), flag `discourse_data_sparse = true` instead of computing a misleadingly precise distribution.

**Step 6.** Write discourse vectors and sparse-flags back to `constituency_features`.

**Exit condition:** Every constituency has either a discourse vector or an explicit sparse-data flag — never a silently empty field.

---

## Phase 5: Clustering & Persona Definition (Week 4, first half)

**Step 1.** Select the feature set for clustering (electoral + demographic + scheme + discourse vectors), standardize with `StandardScaler`.

**Step 2.** Run K-means across k=3 to k=10, compute silhouette score at each k, pick the k that maximizes it (sanity check against expected range, likely 5-7 for 243 constituencies).

**Step 3.** Fit final clustering, write `cluster_id` back to `constituency_features`.

**Step 4.** For each cluster, compute mean feature values and dominant discourse topics. Write a short, plain-language persona name and one-line description for each — this is a manual, judgment-driven step, do it carefully since it's user-facing copy (PRD Design Requirements).

**Step 5.** Store persona names/descriptions in a small `cluster_personas` table keyed by cluster_id.

**Exit condition:** Every constituency has a cluster_id; every cluster has a named persona with a one-line description ready for display.

---

## Phase 6: Validation Against Ground Truth (Week 4, second half)

**Step 1.** Cross-tabulate cluster_id against actual 2025 winning party. Compute the % concentration of the dominant party per cluster.

**Step 2.** Identify clusters with high party concentration (>65%) — these are your strongest validation evidence. Identify clusters near 50/50 — these are genuinely competitive, label them as such rather than treating low concentration as a clustering failure.

**Step 3.** Write the validation table to Supabase and to `docs/validation_results.md` with your interpretation of each cluster's political meaning.

**Step 4.** If clustering looks weak (no cluster above ~55% concentration anywhere), go back to Phase 5 Step 1 and reconsider the feature set or k before moving forward — don't proceed on a segmentation that doesn't show real signal.

**Exit condition:** Validation table exists, reviewed, and you can articulate in plain language why each cluster's composition makes political sense.

---

## Phase 7: Messaging Recommendation Engine (Week 5)

**Step 1.** Write the rule-based recommendation function per the logic sketched in the PRD (scheme-heavy → welfare angle, high anti-incumbency → change narrative, urbanized → governance/development, communal salience → flagged sensitive-handling note). Keep every rule traceable to a specific feature threshold — this is what makes AC5 (traceability) satisfiable.

**Step 2.** Store rule-based recommendations per cluster in a `messaging_recommendations` table.

**Step 3.** (Optional layer) Write the LLM prompt for the nuanced messaging suggestion, call the Claude/Gemini API per cluster, store the output in a separate column (`llm_messaging`) clearly distinct from the rule-based one.

**Step 4.** Manually review every cluster's rule-based and LLM output for obviously bad or insensitive suggestions before this goes anywhere near a UI — especially anything touching the communal/caste discourse flags. This is a manual QA gate, not optional.

**Exit condition:** Every cluster has a reviewed rule-based recommendation; LLM recommendation present and clearly labeled if included.

---

## Phase 8: Backend API — Constituency-Centric (Week 6, first half)

Build these endpoints in this order, since the dossier endpoint is the actual product:

**Step 1.** `GET /api/constituencies` — list all constituencies (id, name, district, cluster_id) for search/autocomplete.

**Step 2.** `GET /api/constituency/{id}` — the core dossier endpoint. Returns the full joined payload: electoral history (2025+2020), demographics, scheme data with confidence flags, discourse topics with sparse-data flag, cluster assignment + persona description, messaging recommendation (rule-based + optional LLM), and source/date labels per section (PRD FR15).

**Step 3.** `GET /api/cluster/{id}` — cluster profile and member list, used for the "similar constituencies" section of the dossier.

**Step 4.** `GET /api/compare?ids=1,2,3` — comparison payload for 2-5 constituencies, same fields as the dossier endpoint but shaped for side-by-side display.

**Step 5.** `GET /api/constituency/{id}/export` — triggers PDF generation (see Phase 10) and returns a file or signed URL.

**Step 6.** Write a basic test for each endpoint using 3-5 known constituencies, manually verifying the returned numbers against your source data (this doubles as early legwork for AC6).

**Exit condition:** All endpoints return correct, complete payloads for a spot-checked sample of constituencies.

---

## Phase 9: Frontend — Constituency Dossier Page (Week 6 second half - Week 7)

**Step 1.** Build the search/autocomplete component hitting `/api/constituencies`.

**Step 2.** Build the dossier page layout per the PRD Design Requirements — section order: header (current result, margin, swing) → electoral history → demographics → scheme exposure → discourse topics → persona/cluster + similar constituencies → messaging recommendation.

**Step 3.** Implement confidence-flag badges (district-level estimate, sparse discourse data) as a reusable component — you'll use it in multiple sections.

**Step 4.** Implement the rule-based vs LLM-messaging visual separation (two distinct panels, different styling, LLM panel clearly labeled).

**Step 5.** Wire up source/date labels per data point (small inline citation-style tags, per FR15) — don't leave this for "later," it's an acceptance criterion and easy to forget once the page looks done.

**Exit condition:** A user can search any constituency and see a fully populated, correctly labeled dossier page.

---

## Phase 10: PDF Export (Week 7, parallel with Step 9 if time allows)

**Step 1.** Decide on rendering approach — headless-browser print-to-PDF of the dossier page (simplest, reuses your existing layout) vs a separate templated PDF (more control, more work). Default to the headless-browser approach for v1.

**Step 2.** Build a print-optimized CSS variant of the dossier page (hide interactive elements, ensure page breaks land sensibly between sections).

**Step 3.** Wire the export endpoint to render and return the PDF.

**Step 4.** Test exported PDFs open correctly offline and contain all sections, flags, and source labels intact (AC3).

**Exit condition:** Exporting any constituency produces a clean, complete, offline-readable PDF.

---

## Phase 11: Comparison View (Week 7-8)

**Step 1.** Build a constituency multi-select component (add/remove up to 5).

**Step 2.** Build the side-by-side table layout, metrics as rows, constituencies as columns, per the Design Requirements.

**Step 3.** Add CSV export for the comparison table.

**Exit condition:** Comparing 2-5 constituencies renders correctly and exports to CSV.

---

## Phase 12: Statewide Map (Week 8, lower priority — build after the dossier is solid)

**Step 1.** Build the Leaflet map with constituencies plotted, colored by cluster_id.

**Step 2.** Wire map marker clicks to navigate into the constituency dossier page.

**Step 3.** Add a cluster legend matching the persona names/colors used elsewhere in the UI.

**Exit condition:** Map renders all constituencies correctly and acts as a working entry point into individual dossiers.

---

## Phase 13: QA Against Acceptance Criteria (Week 8, final days)

Go through the PRD's acceptance criteria list one by one and actually test each:

**Step 1.** AC1/AC2: Spot-check a sample of ~25 constituencies (not just your usual 3-5 test ones) for complete, correctly flagged profiles.

**Step 2.** AC3: Export PDFs for the same sample, confirm offline readability and completeness.

**Step 3.** AC4: Test comparison view at 2, 3, and 5 constituencies.

**Step 4.** AC5: Manually trace 5 messaging recommendations back to their underlying feature values, confirm they're not generic.

**Step 5.** AC6: Manually verify 10 constituencies' profiles against raw source data line by line — this is the credibility-critical check, don't skip or rush it.

**Step 6.** AC7: Test search with 10-15 deliberately misspelled/variant constituency names, confirm correct resolution or sensible "did you mean" suggestions.

**Exit condition:** Every acceptance criterion has been explicitly tested, not just assumed to work because the feature was built.

---

## Phase 14: Documentation & Deployment (Week 8, final days)

**Step 1.** Finalize `docs/data_dictionary.md` — every field, its source, date, granularity, and any known limitation.

**Step 2.** Write the case study writeup per the structure from the earlier roadmap (problem, methodology, feature engineering rationale, NLP approach, clustering validation, example dossier walkthrough, limitations).

**Step 3.** Deploy backend (Railway/Render) and frontend (Vercel), confirm production endpoints match local test results.

**Step 4.** Do one final end-to-end pass on the deployed version, not just localhost — search a constituency, view the dossier, export the PDF, run a comparison, on the live URL.

**Exit condition:** Live, deployed tool, full writeup published, ready to share.

---

## Summary Timeline

| Phase | Weeks | Core deliverable |
|---|---|---|
| 0 | Day 1-2 | Repo, Supabase, data dictionary |
| 1 | Week 1 | Raw data acquired |
| 2 | Week 2 | Cleaned, joined master table |
| 3 | Week 3 (first half) | Electoral + demographic features |
| 4 | Week 3 (second half) | Discourse vectors |
| 5 | Week 4 (first half) | Clusters + personas |
| 6 | Week 4 (second half) | Validation against real results |
| 7 | Week 5 | Messaging recommendations |
| 8 | Week 6 (first half) | Backend API, dossier endpoint |
| 9 | Week 6-7 | Frontend dossier page |
| 10 | Week 7 | PDF export |
| 11 | Week 7-8 | Comparison view |
| 12 | Week 8 | Statewide map |
| 13 | Week 8 (final days) | QA against acceptance criteria |
| 14 | Week 8 (final days) | Docs + deployment |

This runs roughly 8 weeks at a steady pace, matching your usual project cadence. The order is deliberate: data correctness (Phases 1-2) and feature/cluster validity (Phases 3-6) come before any UI work, because a polished dossier page built on a bad join or an unvalidated cluster is worse than no dossier page — it just looks credible while being wrong.
