import os
import pandas as pd
import io
from typing import List
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from xhtml2pdf import pisa

from app.db import get_supabase_client

app = FastAPI(
    title="ConstituencyIQ API",
    description="Backend API serving constituency-level intelligence dossiers for campaign strategists.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Source and date metadata (FR15)
SOURCE_METADATA = {
    "electoral": "ECI Bihar Assembly Election Results (2020, 2025)",
    "demographics": "Primary Census Abstract, Census of India (2011)",
    "welfare": "Government Welfare Dashboards (MGNREGA, PMAY, Ujjwala) (2024-2025)",
    "discourse": "Pre-Election News Media Mentions (Sept-Nov 2024)",
    "nfhs": "National Family Health Survey (NFHS-5) (2019-2021)"
}

def fetch_dossier_by_id(ac_no: int):
    supabase = get_supabase_client()
    
    # 1. Fetch constituency master record
    res_const = supabase.table('constituencies').select('*').eq('ac_no', ac_no).execute()
    if not res_const.data:
        raise HTTPException(status_code=404, detail=f"Constituency with ID {ac_no} not found")
    const = res_const.data[0]
    
    # 2. Fetch electoral history
    res_2025 = supabase.table('election_results_2025').select('*').eq('ac_no', ac_no).execute()
    res_2020 = supabase.table('election_results_2020').select('*').eq('ac_no', ac_no).execute()
    
    # 3. Fetch demographics
    res_census = supabase.table('census_demographics').select('*').eq('ac_no', ac_no).execute()
    
    # 4. Fetch schemes
    res_schemes = supabase.table('schemes').select('*').eq('ac_no', ac_no).execute()
    
    # 5. Fetch NFHS-5
    res_nfhs = supabase.table('nfhs_5').select('*').eq('ac_no', ac_no).execute()
    
    # 6. Fetch features (contains cluster_id and discourse vector)
    res_feats = supabase.table('constituency_features').select('*').eq('ac_no', ac_no).execute()
    
    electoral_history = {
        "election_2025": res_2025.data[0] if res_2025.data else None,
        "election_2020": res_2020.data[0] if res_2020.data else None
    }
    
    demographics = res_census.data[0] if res_census.data else None
    schemes = res_schemes.data[0] if res_schemes.data else None
    nfhs = res_nfhs.data[0] if res_nfhs.data else None
    feats = res_feats.data[0] if res_feats.data else {}
    
    # Extract scheme exposure
    scheme_exposure = {}
    if schemes:
        scheme_exposure = {
            "mgnrega_active_job_cards": schemes.get("mgnrega", {}).get("active_job_cards_count") if schemes.get("mgnrega") else None,
            "mgnrega_expenditure_lakhs": schemes.get("mgnrega", {}).get("total_expenditure_lakhs") if schemes.get("mgnrega") else None,
            "pmay_homes_sanctioned": schemes.get("pmay", {}).get("homes_sanctioned_count") if schemes.get("pmay") else None,
            "pmay_homes_completed": schemes.get("pmay", {}).get("homes_completed_count") if schemes.get("pmay") else None,
            "ujjwala_gas_connections": schemes.get("ujjwala", {}).get("gas_connections_count") if schemes.get("ujjwala") else None,
            "mgnrega_penetration_pct": feats.get("mgnrega_penetration_pct"),
            "pmay_completion_rate": feats.get("pmay_completion_rate"),
            "pmay_penetration_pct": feats.get("pmay_penetration_pct"),
            "ujjwala_penetration_pct": feats.get("ujjwala_penetration_pct"),
            "scheme_penetration_score": feats.get("scheme_penetration_score"),
            "scheme_data_is_district_estimate": feats.get("scheme_data_is_district_estimate", False)
        }
        
    # Extract discourse topics
    discourse_topics = {
        "discourse_data_sparse": feats.get("discourse_data_sparse", True),
        "topics": {
            "inflation": feats.get("discourse_pct_inflation"),
            "communal": feats.get("discourse_pct_communal"),
            "development": feats.get("discourse_pct_development"),
            "welfare": feats.get("discourse_pct_welfare"),
            "caste": feats.get("discourse_pct_caste"),
            "unemployment": feats.get("discourse_pct_unemployment"),
            "other": feats.get("discourse_pct_other")
        }
    }
    
    # 7. Fetch cluster personas & recommendations
    cluster_assignment = None
    messaging_recommendation = None
    
    cluster_id = feats.get("cluster_id")
    if cluster_id is not None:
        res_persona = supabase.table('cluster_personas').select('*').eq('cluster_id', cluster_id).execute()
        res_rec = supabase.table('messaging_recommendations').select('*').eq('cluster_id', cluster_id).execute()
        
        if res_persona.data:
            cluster_assignment = {
                "cluster_id": int(cluster_id),
                "persona_name": res_persona.data[0].get("persona_name"),
                "description": res_persona.data[0].get("description")
            }
        if res_rec.data:
            rec = res_rec.data[0]
            messaging_recommendation = {
                "theme_welfare": rec.get("theme_welfare"),
                "theme_change": rec.get("theme_change"),
                "theme_urban": rec.get("theme_urban"),
                "theme_inclusive": rec.get("theme_inclusive"),
                "sensitive_flag": rec.get("sensitive_flag"),
                "recommendation_text": rec.get("recommendation_text"),
                "example_phrasing": rec.get("example_phrasing"),
                "llm_messaging": rec.get("llm_messaging")
            }
            
    # Assemble full payload
    return {
        "id": int(const["ac_no"]),
        "name": const["ac_name"],
        "district": const["district"],
        "state": const["state"],
        "electoral_history": electoral_history,
        "demographics": demographics,
        "scheme_exposure": scheme_exposure,
        "nfhs_indicators": nfhs,
        "discourse_topics": discourse_topics,
        "cluster_assignment": cluster_assignment,
        "messaging_recommendation": messaging_recommendation,
        "metadata": SOURCE_METADATA
    }

@app.get("/api/constituencies")
def get_constituencies():
    """
    List all constituencies (id, name, district, cluster_id) for search/autocomplete.
    """
    supabase = get_supabase_client()
    try:
        res_consts = supabase.table('constituencies').select('ac_no, ac_name, district').execute()
        res_feats = supabase.table('constituency_features').select('ac_no, cluster_id').execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database fetch error: {e}")
        
    df_c = pd.DataFrame(res_consts.data)
    df_f = pd.DataFrame(res_feats.data)
    
    if df_c.empty:
        return []
        
    df_merged = pd.merge(df_c, df_f, on='ac_no', how='left')
    df_merged = df_merged.rename(columns={
        'ac_no': 'id',
        'ac_name': 'name'
    })
    
    # Fill NaN values and convert types
    df_merged['id'] = df_merged['id'].astype(int)
    df_merged['cluster_id'] = df_merged['cluster_id'].apply(lambda x: int(x) if pd.notna(x) else None)
    
    return df_merged.to_dict(orient="records")

@app.get("/api/constituency/{id}")
def get_constituency(id: int):
    """
    Returns the complete dossier for the selected constituency.
    """
    return fetch_dossier_by_id(id)

@app.get("/api/cluster/{id}")
def get_cluster(id: int):
    """
    Returns the cluster details, validation metrics, and a list of member constituencies.
    """
    supabase = get_supabase_client()
    
    # Fetch cluster persona
    res_persona = supabase.table('cluster_personas').select('*').eq('cluster_id', id).execute()
    if not res_persona.data:
        raise HTTPException(status_code=404, detail=f"Cluster with ID {id} not found")
    persona = res_persona.data[0]
    
    # Fetch validation
    res_val = supabase.table('cluster_validation').select('*').eq('cluster_id', id).execute()
    validation = res_val.data[0] if res_val.data else None
    
    # Fetch members of the cluster
    res_members = supabase.table('constituency_features').select('ac_no').eq('cluster_id', id).execute()
    member_ids = [m['ac_no'] for m in res_members.data]
    
    members = []
    if member_ids:
        res_consts = supabase.table('constituencies').select('ac_no, ac_name, district').in_('ac_no', member_ids).execute()
        members = [{
            "id": int(c["ac_no"]),
            "name": c["ac_name"],
            "district": c["district"]
        } for c in res_consts.data]
        
    return {
        "cluster_id": int(id),
        "persona_name": persona.get("persona_name"),
        "description": persona.get("description"),
        "validation": validation,
        "members_count": len(members),
        "members": members
    }

@app.get("/api/compare")
def get_compare(ids: str = Query(..., description="Comma-separated list of constituency IDs")):
    """
    Returns side-by-side comparison dossiers for 2-5 constituencies.
    """
    try:
        id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid format for ids query parameter. Must be comma-separated integers.")
        
    if not (2 <= len(id_list) <= 5):
        raise HTTPException(status_code=400, detail="Comparison requires between 2 and 5 constituency IDs.")
        
    dossiers = []
    for ac_no in id_list:
        try:
            dossiers.append(fetch_dossier_by_id(ac_no))
        except HTTPException as e:
            # Propagate or skip. For comparison, if one is missing, fail the whole request
            raise HTTPException(status_code=404, detail=f"Constituency with ID {ac_no} in comparison list not found.")
            
    return dossiers

@app.get("/api/constituency/{id}/export")
def get_export(id: int):
    """
    Triggers briefing generation and returns an offline-readable PDF summary of the dossier.
    """
    dossier = fetch_dossier_by_id(id)
    
    # Extract sub-sections safely
    eh = dossier.get("electoral_history", {})
    demo = dossier.get("demographics", {})
    se = dossier.get("scheme_exposure", {})
    dt = dossier.get("discourse_topics", {})
    ca = dossier.get("cluster_assignment", {})
    mr = dossier.get("messaging_recommendation", {})
    
    # 2025 and 2020 Winner info
    winner_2025 = eh.get("election_2025") or {}
    winner_2020 = eh.get("election_2020") or {}
    
    # Demographics info
    demog = demo or {}
    caste = demo or {}
    religion = demo or {}
    
    # Build print-optimized HTML content
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: a4;
                margin: 1.5cm;
            }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 9.5pt;
                line-height: 1.45;
                color: #1e293b;
            }}
            .header {{
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #6366f1;
            }}
            .title {{
                font-size: 20pt;
                font-weight: bold;
                color: #1e1b4b;
            }}
            .subtitle {{
                font-size: 11pt;
                color: #475569;
                margin-top: 5px;
            }}
            h2 {{
                font-size: 13pt;
                font-weight: bold;
                color: #4f46e5;
                margin-top: 15px;
                margin-bottom: 8px;
                border-bottom: 1px solid #cbd5e1;
                padding-bottom: 3px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 12px;
            }}
            th {{
                background-color: #f8fafc;
                font-weight: bold;
                text-align: left;
                padding: 6px 8px;
                border-bottom: 1px solid #cbd5e1;
                font-size: 9pt;
            }}
            td {{
                padding: 6px 8px;
                border-bottom: 1px solid #e2e8f0;
                font-size: 9pt;
            }}
            .badge {{
                display: inline-block;
                background-color: #fef3c7;
                color: #92400e;
                padding: 2px 5px;
                font-size: 7.5pt;
                font-weight: bold;
                border-radius: 4px;
                margin-bottom: 5px;
            }}
            .badge-success {{
                background-color: #d1fae5;
                color: #065f46;
            }}
            .citation {{
                font-size: 7.5pt;
                color: #64748b;
                margin-top: 4px;
                font-style: italic;
            }}
            .recommendation-box {{
                background-color: #f8fafc;
                border-left: 3px solid #3b82f6;
                padding: 8px 12px;
                margin-top: 8px;
            }}
            .ai-box {{
                background-color: #eff6ff;
                border-left: 3px solid #8b5cf6;
                padding: 8px 12px;
                margin-top: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">{dossier.get('name', 'N/A').upper()} CONSTITUENCY DOSSIER</div>
            <div class="subtitle">
                Assembly Constituency No: {dossier.get('id')} | District: {dossier.get('district')} | State: {dossier.get('state')}
            </div>
        </div>
        
        <h2>1. Electoral History & Swing Trends</h2>
        <table>
            <thead>
                <tr>
                    <th>Election Year</th>
                    <th>Winner Candidate</th>
                    <th>Winning Party</th>
                    <th>Margin of Victory</th>
                    <th>Turnout (%)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>2025 (Current)</td>
                    <td>{winner_2025.get('winner_name', 'N/A')}</td>
                    <td>{winner_2025.get('winner_party', 'N/A')}</td>
                    <td>{winner_2025.get('margin', 'N/A')} votes</td>
                    <td>{winner_2025.get('voter_turnout_pct', 'N/A')}%</td>
                </tr>
                <tr>
                    <td>2020 (Prior)</td>
                    <td>{winner_2020.get('winner_name', 'N/A')}</td>
                    <td>{winner_2020.get('winner_party', 'N/A')}</td>
                    <td>{winner_2020.get('margin', 'N/A')} votes</td>
                    <td>{winner_2020.get('voter_turnout_pct', 'N/A')}%</td>
                </tr>
            </tbody>
        </table>
        <div class="citation">Source: {dossier['metadata']['electoral']}</div>

        <h2>2. Demographic Profile</h2>
        <table>
            <tbody>
                <tr>
                    <td><strong>Total Population:</strong> {demog.get('total_population', 'N/A')}</td>
                    <td><strong>Literacy Rate:</strong> {demog.get('literacy_rate_pct', 'N/A')}%</td>
                </tr>
                <tr>
                    <td><strong>Urban Population Share:</strong> {demog.get('urban_ratio_pct', 'N/A')}%</td>
                    <td><strong>Rural Population Share:</strong> {demog.get('rural_ratio_pct', 'N/A')}%</td>
                </tr>
                <tr>
                    <td><strong>Scheduled Caste (SC) %:</strong> {caste.get('sc_ratio_pct', 'N/A')}%</td>
                    <td><strong>Scheduled Tribe (ST) %:</strong> {caste.get('st_ratio_pct', 'N/A')}%</td>
                </tr>
                <tr>
                    <td><strong>Religious Share: Hindu:</strong> {religion.get('hindu_ratio_pct', 'N/A')}%</td>
                    <td><strong>Religious Share: Muslim:</strong> {religion.get('muslim_ratio_pct', 'N/A')}%</td>
                </tr>
            </tbody>
        </table>
        <div class="citation">Source: {dossier['metadata']['demographics']}</div>

        <h2>3. Welfare Scheme Exposure</h2>
        {f'<div class="badge">CONFIDENCE: DISTRICT ESTIMATE AVERAGE</div>' if se.get('scheme_data_is_district_estimate') else f'<div class="badge badge-success">CONFIDENCE: TRUE CONSTITUENCY DATA</div>'}
        <table>
            <tbody>
                <tr>
                    <td><strong>Active MGNREGA Job Cards:</strong> {se.get('mgnrega_active_job_cards', 'N/A')}</td>
                    <td><strong>PMAY Homes Completed:</strong> {se.get('pmay_homes_completed', 'N/A')} (out of {se.get('pmay_homes_sanctioned', 'N/A')} sanctioned)</td>
                </tr>
                <tr>
                    <td><strong>Ujjwala Gas Connections:</strong> {se.get('ujjwala_gas_connections', 'N/A')}</td>
                    <td><strong>Composite Scheme Score:</strong> {se.get('scheme_penetration_score', 'N/A')}</td>
                </tr>
            </tbody>
        </table>
        <div class="citation">Source: {dossier['metadata']['welfare']}</div>

        <h2>4. Local News Discourse Topics</h2>
        {f'<div class="badge">COVERAGE: SPARSE MEDIA MENTIONS</div>' if dt.get('discourse_data_sparse') else f'<div class="badge badge-success">COVERAGE: COMPLETE MEDIA DATA</div>'}
        <table>
            <thead>
                <tr>
                    <th>Topic Category</th>
                    <th>Share (%)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Infrastructure & Development</td>
                    <td>{f"{dt['topics']['development']:.2f}%" if dt['topics'].get('development') is not None else 'N/A'}</td>
                </tr>
                <tr>
                    <td>Welfare & Schemes</td>
                    <td>{f"{dt['topics']['welfare']:.2f}%" if dt['topics'].get('welfare') is not None else 'N/A'}</td>
                </tr>
                <tr>
                    <td>Unemployment & Jobs</td>
                    <td>{f"{dt['topics']['unemployment']:.2f}%" if dt['topics'].get('unemployment') is not None else 'N/A'}</td>
                </tr>
                <tr>
                    <td>Campaign Trails & Other</td>
                    <td>{f"{dt['topics']['other']:.2f}%" if dt['topics'].get('other') is not None else 'N/A'}</td>
                </tr>
            </tbody>
        </table>
        <div class="citation">Source: {dossier['metadata']['discourse']}</div>

        <div style="page-break-after: always;"></div>

        <h2>5. Strategic Segment & Persona</h2>
        {f'<h3>Persona: {ca.get("persona_name")} (Cluster {ca.get("cluster_id")})</h3>' if ca else ''}
        <p>{ca.get("description") if ca else "N/A"}</p>
        
        <h2>6. Campaign Messaging Recommendations</h2>
        {f'<div class="badge">SENSITIVE LANDSCAPE FLAG ACTIVE</div>' if mr.get('sensitive_flag') else ''}
        
        <div class="recommendation-box">
            <strong>Rule-Based Strategy (Traceable):</strong><br/>
            {mr.get('recommendation_text', 'N/A')}
            <br/><br/>
            <strong>Example Slogan / Phrasing:</strong><br/>
            <em>{mr.get('example_phrasing', 'N/A')}</em>
        </div>

        <div class="ai-box">
            <strong>AI Suggested Nuanced Messaging:</strong><br/>
            {mr.get('llm_messaging', 'N/A')}
        </div>
    </body>
    </html>
    """
    
    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(html_content, dest=pdf_buffer)
    pdf_data = pdf_buffer.getvalue()
    pdf_buffer.close()
    
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=constituency_{id}_dossier.pdf"}
    )

_cached_spatial_geojson = None

@app.get("/api/spatial")
def get_spatial():
    global _cached_spatial_geojson
    if _cached_spatial_geojson is not None:
        return _cached_spatial_geojson
        
    import json
    
    supabase = get_supabase_client()
    try:
        res_feats = supabase.table('constituency_features').select('*').execute()
        res_personas = supabase.table('cluster_personas').select('cluster_id, persona_name').execute()
        res_results = supabase.table('election_results_2025').select('ac_no, winner_name, winner_party, margin, voter_turnout_pct').execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database fetch error: {e}")
        
    persona_map = {int(p['cluster_id']): p['persona_name'] for p in res_personas.data if p.get('cluster_id') is not None}
    feats_map = {int(f['ac_no']): f for f in res_feats.data if f.get('ac_no') is not None}
    results_map = {int(r['ac_no']): r for r in res_results.data if r.get('ac_no') is not None}
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    spatial_dir = os.path.join(base_dir, "data", "raw", "spatial")
    features = []
    
    if os.path.exists(spatial_dir):
        for filename in sorted(os.listdir(spatial_dir)):
            if filename.endswith(".geojson") and filename.startswith("AC"):
                filepath = os.path.join(spatial_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        feature = json.load(f)
                        # Inject cluster and metrics data
                        props = feature.get("properties", {})
                        ac_no = props.get("ac_no")
                        if ac_no is not None:
                            ac_no = int(ac_no)
                            
                            # Results data
                            if ac_no in results_map:
                                r = results_map[ac_no]
                                props["winner_name"] = r.get("winner_name")
                                props["winner_party"] = r.get("winner_party")
                                props["margin"] = r.get("margin")
                                props["voter_turnout_pct"] = r.get("voter_turnout_pct")
                            else:
                                props["winner_name"] = "N/A"
                                props["winner_party"] = "N/A"
                                props["margin"] = None
                                props["voter_turnout_pct"] = None
                                
                            # Features data
                            if ac_no in feats_map:
                                ft = feats_map[ac_no]
                                cid = ft.get("cluster_id")
                                props["cluster_id"] = int(cid) if cid is not None else None
                                props["persona_name"] = persona_map.get(int(cid)) if cid is not None else 'Unassigned'
                                props["competitiveness_score"] = ft.get("competitiveness_score")
                                props["turnout_delta"] = ft.get("turnout_delta")
                                props["scheme_penetration_score"] = ft.get("scheme_penetration_score")
                            else:
                                props["cluster_id"] = None
                                props["persona_name"] = "Unassigned"
                                props["competitiveness_score"] = None
                                props["turnout_delta"] = None
                                props["scheme_penetration_score"] = None
                                
                        features.append(feature)
                except Exception as e:
                    print(f"Error loading spatial file {filename}: {e}")
                    
    _cached_spatial_geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return _cached_spatial_geojson

@app.get("/api/debug")
def get_debug():
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    spatial_dir = os.path.join(base_dir, "data", "raw", "spatial")
    exists = os.path.exists(spatial_dir)
    files = os.listdir(spatial_dir) if exists else []
    return {
        "__file__": __file__,
        "abspath": os.path.abspath(__file__),
        "getcwd": os.getcwd(),
        "base_dir": base_dir,
        "spatial_dir": spatial_dir,
        "exists": exists,
        "files_count": len(files),
        "files_sample": files[:5] if files else []
    }
