# PRD: Constituency Intelligence Dossier (Voter Segmentation + Constituency Deep-Dive)

**Working name:** ConstituencyIQ
**Owner:** Shadwal
**Status:** Draft v2 — reframed around constituency-level intelligence for political end users
**Scope:** Bihar Assembly Election 2025 (extensible to other states/elections)

---

## Problem Statement

When a politician or campaign strategist is assigned to or contesting a specific constituency, the actual information they need is scattered across a dozen disconnected sources: ECI result PDFs, decade-old Census tables, district welfare scheme dashboards, scattered local news coverage, and whatever their own ground team verbally reports. There is no single place that compiles everything relevant to *one named constituency* — its electoral history, who actually lives there, what they depend on economically, what they're currently talking about, and how it compares to similar constituencies elsewhere in the state.

This forces strategists to either commission expensive, slow consultancy reports for each constituency, or operate on incomplete ground intuition. Neither scales across 50-200+ constituencies in a state campaign, and neither is reproducible or auditable.

## Goal

Build a tool where a strategist enters or selects a single constituency and receives a complete, structured intelligence profile for it — demographics, electoral history and trends, welfare/scheme exposure, current local discourse, its persona/cluster relative to other constituencies, and a tailored messaging recommendation — all sourced from public data, in one screen, in under a few seconds.

Success is defined as: a strategist with zero data science background can pull up any constituency in the covered state and get an answer to "what do I need to know about this seat" without leaving the tool or commissioning outside analysis.

## Target User

- **Primary:** Political strategists and campaign data teams responsible for a specific constituency or set of constituencies — the people deciding messaging, ad allocation, and ground outreach for a seat.
- **Primary:** Contesting politicians/candidates themselves who want a fast, credible briefing on their own constituency (and rival/neighboring constituencies) without relying on secondhand ground reports.
- **Secondary:** State-level campaign coordinators who need to compare constituencies side by side to allocate resources across a whole state.
- **Tertiary (build/validation phase):** Shadwal, as the builder validating the data pipeline and methodology before any real strategist sees it.

This is explicitly *not* built for end voters, journalists, or the general public in v1 — the framing, language, and depth of data assume a user making campaign decisions.

## User Stories

1. As a strategist, I want to search or select a single constituency by name and get a full profile instantly, so I don't have to manually assemble data from five different government portals.
2. As a candidate, I want to see my constituency's full electoral history (2020 vs 2025: vote share, margin, turnout, swing) on one screen, so I understand my actual position before deciding strategy.
3. As a strategist, I want to see the demographic composition of a constituency (literacy, urban/rural split, religion, SC/ST %, occupation mix), so I can tailor messaging to who actually lives there.
4. As a strategist, I want to see welfare scheme penetration (MGNREGA, PMAY, Ujjwala, etc.) for the constituency, so I know whether welfare-delivery messaging is credible there.
5. As a strategist, I want to see what local issues are currently dominant in news/discourse for this specific constituency, so my messaging is responsive to what people are actually talking about, not generic state-level talking points.
6. As a strategist, I want to know which "persona cluster" this constituency falls into and which other constituencies share that persona, so I can reuse a proven messaging strategy across similar seats instead of building one from scratch for each.
7. As a strategist, I want a concrete messaging recommendation specific to this constituency's profile, with example phrasing, so I have an actionable starting point, not just raw data.
8. As a state campaign coordinator, I want to compare two or more constituencies side by side, so I can decide where to allocate limited resources (ad budget, ground staff, candidate visits).
9. As a strategist, I want to export a constituency's full dossier as a PDF/doc, so I can share it with field teams who won't be using the dashboard directly.
10. As a strategist, I want to know what data is missing or low-confidence for a constituency (e.g. no news coverage found, scheme data is district-level only), so I don't mistake a data gap for an actual finding.

## Functional Requirements

**Constituency search & selection**
- FR1: System shall allow searching/selecting any constituency in the covered state by name, with autocomplete/fuzzy matching to handle naming variants.
- FR2: System shall default to showing a ranked/browsable list of all constituencies if no specific search is entered.

**Constituency profile (the core deliverable)**
- FR3: System shall display, for the selected constituency: current and previous representative/winner, party, margin, vote share, and turnout for both the most recent and prior election.
- FR4: System shall display swing metrics: vote share swing, turnout delta, anti-incumbency magnitude, computed automatically from the ingested 2020/2025 results.
- FR5: System shall display full demographic breakdown: population, literacy rate, urban/rural %, SC/ST %, religion composition, occupation mix — sourced from Census data mapped to the constituency.
- FR6: System shall display welfare scheme exposure for the constituency: MGNREGA, PMAY, Ujjwala (minimum set), with beneficiary counts/percentages, and a visible flag when the underlying figure is a district-level estimate rather than constituency-specific.
- FR7: System shall display a ranked list of dominant local discourse topics (inflation, development, communal, welfare, caste, unemployment, etc.) extracted from news coverage tagged to that constituency, with a visible flag when discourse data coverage is sparse.
- FR8: System shall display the constituency's assigned persona/cluster, a plain-language description of that persona, and a list of other constituencies sharing the same persona.
- FR9: System shall display a messaging recommendation specific to the constituency — both a rule-based recommendation (fully traceable to the underlying features) and, optionally, an LLM-generated nuanced version, clearly separated and labeled.

**Comparison & state-level context**
- FR10: System shall allow selecting 2+ constituencies and viewing their core metrics side by side in a comparison table.
- FR11: System shall show, for context, where the selected constituency ranks statewide on key metrics (e.g. "top 10% most competitive seat," "above-median scheme dependency").

**Export & sharing**
- FR12: System shall allow exporting a single constituency's full dossier as a PDF, formatted for sharing with non-dashboard users (ground teams, candidates).
- FR13: System shall allow exporting a comparison table (CSV) for multiple constituencies.

**Map (secondary, supporting view)**
- FR14: System shall provide a statewide map view, color-coded by persona cluster, as a navigation aid into individual constituency profiles — this is a way *into* the per-constituency dossier, not the primary deliverable.

**Data transparency**
- FR15: Every data point in a constituency profile shall be traceable to a labeled source and date (e.g. "Census 2011," "ECI 2025 result," "News coverage, Sept-Nov 2024") so a strategist can judge its currency and reliability.

## Non-Functional Requirements

- NFR1: A full constituency profile shall load in under 2 seconds once the underlying data pipeline has run (the pipeline itself is a backend batch process, not run live per query).
- NFR2: The constituency profile view must be understandable by a non-technical user within 30 seconds of landing on the page — clear headers, no unexplained statistical jargon without a plain-language gloss.
- NFR3: All data sources used shall be public and free; no paid scraping/API infrastructure required for v1.
- NFR4: Cluster and feature computations shall be reproducible — same input data and seed produce identical outputs, so two strategists looking at the same constituency get the same answer.
- NFR5: Rule-based outputs (recommendations, computed metrics) must be visually and structurally distinct from LLM-generated text, to avoid a strategist mistaking a generated suggestion for a hard data point.
- NFR6: No individual voter-level data shall be collected, stored, or inferred — all profiles are constituency-aggregate.
- NFR7: PDF export must be a clean, standalone document — readable without internet access or dashboard context, suitable for printing or forwarding via WhatsApp/email to a ground team.

## User Flow

1. Strategist lands on the tool, sees a search bar and a statewide map.
2. Strategist searches for or clicks a specific constituency (e.g. "Raghopur").
3. Tool loads the constituency's full dossier: header (name, current MLA/winner, party, margin) → electoral history section → demographics section → welfare scheme section → discourse/issues section → persona/cluster section → messaging recommendation section.
4. Strategist reviews data, notes any flagged low-confidence sections (e.g. "discourse data sparse — only 4 articles found").
5. Strategist optionally clicks into the constituency's persona cluster to see a list of similar constituencies, useful if the same campaign is contesting multiple seats with the same profile.
6. Strategist optionally adds a second constituency to a comparison view (e.g. comparing the candidate's seat to a neighboring rival's seat).
7. Strategist exports the dossier as a PDF to forward to the local ground team or candidate.
8. (Optional, less common) Strategist returns to the statewide map to browse other constituencies without a specific name in mind.

## Design Requirements

- The constituency profile page is the primary screen — design it as a structured "briefing document" layout (clear section headers, scannable in order of strategic priority: who's currently winning → why → who lives there → what they need → what to say), not a generic analytics dashboard grid.
- Lead with the electoral header (current result, margin, swing) above the fold — this is what a strategist checks first.
- Use flags/badges consistently for data confidence (e.g. a small "district-level estimate" tag next to scheme figures, "low discourse coverage" tag next to issue rankings) rather than burying caveats in footnotes.
- Persona/cluster name should read as a strategist would describe it informally (e.g. "Welfare-dependent rural, low swing"), not a generic "Cluster 3" label, anywhere it's user-facing.
- LLM-generated messaging suggestions must sit in a visually separate, clearly labeled panel (e.g. "AI-suggested messaging — review before use") distinct from the rule-based recommendation panel.
- Comparison view should align metrics in rows so differences between constituencies are visually scannable, not require re-reading two separate profiles.
- Keep visual tone serious and document-like — this is a working tool for people making real campaign decisions, not a consumer data-viz showcase.

## Technical Constraints

- Stack: FastAPI backend, Supabase/Postgres for storage, React + TypeScript frontend, Leaflet for the supporting map view, scikit-learn for clustering, sentence-transformers/BERTopic for discourse topic extraction, optional Claude/Gemini API call for the LLM messaging layer, a PDF generation library (e.g. WeasyPrint or a headless-browser print-to-PDF) for dossier export.
- Census 2011 is the most recent full public dataset; all demographic figures are over a decade old and must be labeled with their actual source year, not presented as current.
- ECI constituency naming is inconsistent across election years and requires fuzzy matching plus manual verification during the join step — this affects swing calculations and must be resolved before profiles are generated, not at query time.
- Welfare scheme data is frequently available only at district/block level; constituency-level figures will often be a documented allocation estimate, not a direct figure — this must be carried through to the FR6 confidence flag, not silently presented as precise.
- Discourse/news data depends on manual or light-API scraping; constituencies with low media coverage (common for smaller/rural seats) will have sparse discourse data — the system must degrade gracefully (FR7 flag) rather than fabricate topic distributions.
- PDF export must work without requiring the underlying database to be live (i.e. it should be a rendered snapshot, not a live-query document), so it can be shared and viewed offline.

## Edge Cases

- A constituency has no matched news articles → discourse section shows an explicit "insufficient discourse data for this constituency" message instead of an empty chart or a misleadingly confident topic ranking.
- A constituency's boundaries changed since the prior election (delimitation) → swing metrics are flagged as "not directly comparable" rather than silently computed.
- Welfare scheme data exists only at district level for a given constituency → all scheme figures in that profile show the "district-level estimate" flag, and the strategist can see which district the estimate is drawn from.
- Two constituencies have very similar names (common across Indian states) → search must disambiguate clearly (showing district alongside name) rather than risk loading the wrong profile.
- A constituency is in a persona cluster with only one member (no similar seats) → still display its full profile normally, but the "similar constituencies" section explicitly states it has no cluster peers rather than showing an empty or broken list.
- User exports a PDF for a constituency mid-pipeline-update (data partially refreshed) → export should pull from the last fully-completed data snapshot, not a partially updated state, to avoid an internally inconsistent document.
- Strategist searches for a constituency name that doesn't exist in the covered state (typo or wrong state) → return a clear "not found" with suggested closest matches, not a silent empty page.

## Acceptance Criteria

- AC1: Given any valid constituency name in the covered state, the tool returns a complete profile containing electoral history, demographics, scheme exposure, discourse topics, cluster assignment, and messaging recommendation, each with a visible source/date label.
- AC2: At least 95% of constituencies in the covered state return a profile with no missing core sections (demographics and electoral history are mandatory; discourse and scheme data may carry a "low confidence" flag but must not be blank without explanation).
- AC3: PDF export of any constituency profile renders correctly with all sections, source labels, and confidence flags intact, and opens correctly offline.
- AC4: Comparison view correctly aligns and displays metrics for at least 2 and up to 5 constituencies simultaneously without layout breakage.
- AC5: Every messaging recommendation shown is traceable to specific underlying feature values for that constituency (no generic, non-constituency-specific text).
- AC6: A test set of 10 constituencies, manually checked by the builder against source data, shows no factual mismatches between the profile and the underlying public records.
- AC7: Search correctly resolves at least 95% of constituency name variants/misspellings to the correct constituency in a manual test of common naming variants.

## Out of Scope

- Individual voter-level targeting or any personally identifiable voter data — all profiles remain constituency-aggregate.
- Live/real-time discourse monitoring during an active campaign — v1 is a point-in-time intelligence tool built from a defined data snapshot, not a live feed.
- Direct integration with ad platforms or ground-outreach tools (no automated ad delivery or CRM integration) — output is a briefing document and recommendation, not an execution system.
- Forecasting the outcome of a future, not-yet-held election — v1 profiles and validates against a past, known result; predictive forecasting for an upcoming election is a distinct, separately scoped problem.
- Multi-state coverage in v1 — ships for one state (Bihar) first; architecture should allow extension but v1 does not support cross-state comparison.
- Booth-level granularity — v1 operates at constituency level; booth-level profiles are a documented future extension.
- Paid Twitter/X API integration — explicitly excluded from v1 due to cost; discourse analysis runs on news article data only.
- User accounts, role-based access, or multi-tenant party-specific data isolation — v1 is a single-instance tool for the builder's own use and demonstration, not a multi-campaign SaaS product.
