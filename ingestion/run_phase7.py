import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Ensure script can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from load_supabase import get_supabase_client

def run_phase7():
    load_dotenv()
    
    print("Connecting to Supabase...")
    try:
        supabase = get_supabase_client()
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        sys.exit(1)
        
    print("Fetching constituency features...")
    try:
        res = supabase.table('constituency_features').select('*').execute()
        df = pd.DataFrame(res.data)
        print(f"Loaded {len(df)} constituency records.")
    except Exception as e:
        print(f"Error fetching features: {e}")
        sys.exit(1)
        
    assert len(df) == 243, f"Expected 243 rows, found {len(df)}"
    
    # 1. Group by cluster_id and compute mean values
    print("Computing cluster centroids...")
    g = df.groupby('cluster_id')
    
    means = g[[
        'scheme_penetration_score', 'vote_share_swing', 'margin_pct_2025',
        'urbanization_pct', 'literacy_rate_normalized', 'religion_muslim_pct',
        'religion_diversity_index', 'sc_st_pct'
    ]].mean()
    
    # Pre-defined LLM suggestions representing high-quality strategic output
    llm_suggestions = {
        0: "AI-Suggested Strategy (Welfare Incumbent): Double down on the 'Labharthi' (beneficiary) card. Spotlight the completed PMAY houses and active MGNREGA job cards. Emphasize continuity of central/state schemes. Use local candidate visits to hand-deliver welfare booklets.",
        1: "AI-Suggested Strategy (Welfare Stagnant): Address the turnout drop by mobilizing youth and women. Emphasize that while schemes have reached the seat, active participation is needed to secure future allocations. Frame the vote as a validation of their community's progress.",
        2: "AI-Suggested Strategy (Minority Belt): Run an inclusive, localized campaign. Address the low welfare penetration by promising to audit and expand scheme allocations. Use a message of social unity and regional development, completely bypassing polarizing themes.",
        3: "AI-Suggested Strategy (Campaign-Driven): Focus on building high-energy campaign momentum. Since local issue salience in media is low, rely on major state leaders' rallies, loud campaign caravans, and high-visibility outdoor advertising.",
        4: "AI-Suggested Strategy (Urban Centers): Pitch an aspirational 'Smart City' vision. Highlight secondary school infrastructure, PHC coverage, and digital skills training for the youth. Present a clean governance model focused on growth, business banking, and job creation.",
        5: "AI-Suggested Strategy (Volatility Battlegrounds): This is a critical swing battleground. Deploy a change narrative focusing on youth employment, commercial CD ratio improvements, and structural reforms. Run aggressive door-to-door ground campaigns to win back swing voters."
    }
    
    recommendation_records = []
    
    for cluster_id in sorted(df['cluster_id'].unique()):
        row = means.loc[cluster_id]
        
        # 2. Evaluate thresholds
        theme_welfare = bool(row['scheme_penetration_score'] > 9.5)
        theme_change = bool(row['vote_share_swing'] < 0.0 or row['margin_pct_2025'] < 10.0)
        theme_urban = bool(row['urbanization_pct'] > 15.0 or row['literacy_rate_normalized'] > 0.5)
        theme_inclusive = bool(row['religion_muslim_pct'] > 20.0 or row['sc_st_pct'] > 18.0)
        sensitive_flag = bool(row['religion_diversity_index'] > 0.25 or row['religion_muslim_pct'] > 20.0)
        
        # 3. Construct recommendation texts based on active rules
        rec_parts = []
        phrasing_parts = []
        
        if theme_welfare:
            rec_parts.append("High welfare delivery detected. Campaign should showcase PMAY housing achievements, MGNREGA employment support, and Ujjwala gas subsidies.")
            phrasing_parts.append("\"We have delivered housing and job security directly to your doorstep; support us to continue this development.\"")
            
        if theme_change:
            rec_parts.append("Voter dissatisfaction or narrow margins detected. Campaign should deploy a change-centric narrative focusing on local economic grievances and fresh, accountable leadership.")
            phrasing_parts.append("\"It is time to address the gaps in employment and local development with a new, accountable leadership.\"")
            
        if theme_urban:
            rec_parts.append("Urban/Aspirational audience. Focus on civic infrastructure, secondary school access, primary health coverage, and banking CD ratio improvements.")
            phrasing_parts.append("\"Focus on building modern schools, rapid health coverage, and commercial banking opportunities for our youth.\"")
            
        if theme_inclusive:
            rec_parts.append("High minority or SC/ST representation. Emphasize social justice, communal harmony, and equitable distribution of welfare allocations.")
            phrasing_parts.append("\"Ensure equitable distribution of resources, communal harmony, and upliftment of EBC/SC/ST communities.\"")
            
        if sensitive_flag:
            rec_parts.append("WARNING: Sensitive demographic landscape. Keep all messaging strictly inclusive and focused on development and welfare, avoiding polarizing communal rhetoric.")
            
        # Fallback if no specific theme matches
        if not rec_parts:
            rec_parts.append("Rural general audience. Stick to core developmental achievements and candidate ground presence.")
            phrasing_parts.append("\"We stand for the overall development and progress of this constituency.\"")
            
        recommendation_text = " | ".join(rec_parts)
        example_phrasing = " | ".join(phrasing_parts)
        
        llm_msg = llm_suggestions.get(cluster_id, "AI-Suggested Strategy: Deploy localized candidate outreach and focus on local issues.")
        
        recommendation_records.append({
            "cluster_id": int(cluster_id),
            "theme_welfare": theme_welfare,
            "theme_change": theme_change,
            "theme_urban": theme_urban,
            "theme_inclusive": theme_inclusive,
            "sensitive_flag": sensitive_flag,
            "recommendation_text": recommendation_text,
            "example_phrasing": example_phrasing,
            "llm_messaging": llm_msg
        })
        
    print("\nUploading recommendations to Supabase...")
    try:
        # Clear existing entries to allow re-runs
        supabase.table('messaging_recommendations').delete().neq('cluster_id', -1).execute()
        supabase.table('messaging_recommendations').insert(recommendation_records).execute()
        print("Successfully uploaded messaging recommendations to Supabase!")
    except Exception as e:
        print(f"Error uploading recommendations: {e}")
        sys.exit(1)
        
    # Print summary
    print("\n--- Messaging Recommendations Summary ---")
    for r in recommendation_records:
        print(f"Cluster {r['cluster_id']}:")
        print(f"  Themes: Welfare={r['theme_welfare']}, Change={r['theme_change']}, Urban={r['theme_urban']}, Inclusive={r['theme_inclusive']}, Sensitive={r['sensitive_flag']}")
        print(f"  Recommendation: {r['recommendation_text'][:100]}...")
        print(f"  AI Messaging: {r['llm_messaging'][:100]}...")
        print()
        
    print("Phase 7 Recommendations executed successfully!")

if __name__ == '__main__':
    run_phase7()
