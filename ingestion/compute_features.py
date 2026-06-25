import json
import numpy as np
import pandas as pd

def extract_winner_vote_share(candidates_str, winner_name):
    if not candidates_str:
        return None
    try:
        if isinstance(candidates_str, str):
            candidates = json.loads(candidates_str)
        else:
            candidates = candidates_str
        
        # Find candidate whose name is winner_name
        for c in candidates:
            if c.get('candidate_name') == winner_name:
                return c.get('vote_share_pct')
        # Fallback to max vote share
        if candidates:
            return max(c.get('vote_share_pct', 0) for c in candidates)
    except Exception as e:
        print(f"Error parsing candidates for winner {winner_name}: {e}")
    return None

def extract_party_vote_share(candidates_str, party_name):
    if not candidates_str or not party_name:
        return 0.0
    try:
        if isinstance(candidates_str, str):
            candidates = json.loads(candidates_str)
        else:
            candidates = candidates_str
        
        party_shares = [c.get('vote_share_pct', 0.0) for c in candidates if c.get('party') == party_name]
        if party_shares:
            return sum(party_shares)
    except Exception as e:
        print(f"Error parsing candidates for party {party_name}: {e}")
    return 0.0

def compute_effective_candidates(candidates_str):
    if not candidates_str:
        return 1.0
    try:
        if isinstance(candidates_str, str):
            candidates = json.loads(candidates_str)
        else:
            candidates = candidates_str
        
        shares = [c.get('vote_share_pct', 0.0) / 100.0 for c in candidates if c.get('vote_share_pct') is not None]
        sum_sq = sum(s ** 2 for s in shares)
        if sum_sq > 0:
            return 1.0 / sum_sq
    except Exception as e:
        print(f"Error parsing candidates for effective candidates: {e}")
    return 1.0

def compute_electoral_features(df_2025: pd.DataFrame, df_2020: pd.DataFrame) -> pd.DataFrame:
    """
    Computes electoral features: turnout delta, winner vote share 2025/2020,
    vote share swing (compares winning party's share), margins, competitiveness,
    effective candidates (Laakso-Taagepera), and anti-incumbency magnitude.
    """
    # Merge datasets on ac_no
    merged = pd.merge(
        df_2025, 
        df_2020, 
        on='ac_no', 
        suffixes=('_2025', '_2020')
    )
    
    features_list = []
    for _, row in merged.iterrows():
        ac_no = row['ac_no']
        
        # Turnout
        t_2025 = row['voter_turnout_pct_2025']
        t_2020 = row['voter_turnout_pct_2020']
        turnout_delta = t_2025 - t_2020
        
        # Winner vote share
        winner_name_2025 = row['winner_name_2025']
        winner_name_2020 = row['winner_name_2020']
        
        ws_2025 = extract_winner_vote_share(row['candidates_2025'], winner_name_2025)
        ws_2020 = extract_winner_vote_share(row['candidates_2020'], winner_name_2020)
        
        # Vote share swing of the 2025 winning party
        winner_party_2025 = row['winner_party_2025']
        wp_share_2025 = ws_2025 if ws_2025 is not None else 0.0
        wp_share_2020 = extract_party_vote_share(row['candidates_2020'], winner_party_2025)
        vote_share_swing = wp_share_2025 - wp_share_2020
        
        # Margins
        margin_2025 = row['margin_2025']
        total_votes_2025 = row['total_polled_votes_2025']
        margin_pct_2025 = (margin_2025 / total_votes_2025 * 100.0) if total_votes_2025 > 0 else 0.0
        
        margin_2020 = row['margin_2020']
        total_votes_2020 = row['total_polled_votes_2020']
        margin_pct_2020 = (margin_2020 / total_votes_2020 * 100.0) if total_votes_2020 > 0 else 0.0
        
        margin_pct_delta = margin_pct_2025 - margin_pct_2020
        
        # Competitiveness
        competitiveness_score = 100.0 - margin_pct_2025
        
        # Effective candidates
        eff_cand = compute_effective_candidates(row['candidates_2025'])
        
        # Anti-incumbency
        winner_party_2020 = row['winner_party_2020']
        party_flipped = 1 if winner_party_2025 != winner_party_2020 else 0
        
        if party_flipped == 1:
            anti_incumbency_magnitude = abs(margin_pct_2025)
        else:
            anti_incumbency_magnitude = -margin_pct_delta
            
        features_list.append({
            'ac_no': int(ac_no),
            'turnout_delta': turnout_delta,
            'winner_vote_share_2025': ws_2025,
            'winner_vote_share_2020': ws_2020,
            'vote_share_swing': vote_share_swing,
            'margin_pct_2025': margin_pct_2025,
            'margin_pct_2020': margin_pct_2020,
            'margin_pct_delta': margin_pct_delta,
            'competitiveness_score': competitiveness_score,
            'effective_candidates': eff_cand,
            'anti_incumbency_flag': party_flipped,
            'anti_incumbency_magnitude': anti_incumbency_magnitude
        })
        
    return pd.DataFrame(features_list)

def compute_demographic_features(df_census: pd.DataFrame) -> pd.DataFrame:
    """
    Computes demographic features: literacy z-score, urbanization, sc/st %,
    agriculture dependency %, and religion diversity index.
    """
    df = df_census.copy()
    
    # Literacy z-score
    lit_mean = df['literacy_rate_pct'].mean()
    lit_std = df['literacy_rate_pct'].std()
    # Avoid ZeroDivisionError
    lit_std = lit_std if lit_std > 0 else 1.0
    df['literacy_rate_normalized'] = (df['literacy_rate_pct'] - lit_mean) / lit_std
    
    # Urbanization
    df['urbanization_pct'] = df['urban_ratio_pct']
    
    # SC/ST %
    df['sc_st_pct'] = df['sc_ratio_pct'] + df['st_ratio_pct']
    
    # Agriculture Dependency %
    ag_numerator = df['cultivators_count'] + df['agricultural_laborers_count']
    ag_denominator = (
        df['cultivators_count'] + 
        df['agricultural_laborers_count'] + 
        df['household_industry_workers_count'] + 
        df['other_workers_count'] + 
        df['non_workers_count']
    )
    df['agriculture_dependency_pct'] = np.where(
        ag_denominator > 0,
        (ag_numerator / ag_denominator) * 100.0,
        0.0
    )
    
    # Religion Passthroughs
    df['religion_hindu_pct'] = df['hindu_ratio_pct']
    df['religion_muslim_pct'] = df['muslim_ratio_pct']
    df['religion_other_pct'] = df['other_religion_ratio_pct']
    
    # Religion Diversity Index (Herfindahl complement: 1 - sum(p_i^2))
    p_hindu = df['religion_hindu_pct'] / 100.0
    p_muslim = df['religion_muslim_pct'] / 100.0
    p_other = df['religion_other_pct'] / 100.0
    df['religion_diversity_index'] = 1.0 - (p_hindu**2 + p_muslim**2 + p_other**2)
    
    # Select final columns
    cols = [
        'ac_no', 'literacy_rate_normalized', 'urbanization_pct', 'sc_st_pct',
        'agriculture_dependency_pct', 'religion_hindu_pct', 'religion_muslim_pct',
        'religion_other_pct', 'religion_diversity_index'
    ]
    return df[cols]

def compute_scheme_features(df_schemes: pd.DataFrame, df_census: pd.DataFrame) -> pd.DataFrame:
    """
    Computes scheme features: population-normalized penetration for MGNREGA/PMAY/Ujjwala,
    PMAY completion rate, and composite scheme penetration score.
    """
    # Merge with census to get total_population
    merged = pd.merge(
        df_schemes,
        df_census[['ac_no', 'total_population']],
        on='ac_no'
    )
    
    # MGNREGA active cards per-capita %
    merged['mgnrega_penetration_pct'] = np.where(
        merged['total_population'] > 0,
        (merged['mgnrega_active_job_cards'] / merged['total_population']) * 100.0,
        0.0
    )
    
    # PMAY completion rate
    merged['pmay_completion_rate'] = np.where(
        merged['pmay_homes_sanctioned'] > 0,
        (merged['pmay_homes_completed'] / merged['pmay_homes_sanctioned']) * 100.0,
        0.0
    )
    
    # PMAY homes sanctioned per-capita %
    merged['pmay_penetration_pct'] = np.where(
        merged['total_population'] > 0,
        (merged['pmay_homes_sanctioned'] / merged['total_population']) * 100.0,
        0.0
    )
    
    # Ujjwala gas connections per-capita %
    merged['ujjwala_penetration_pct'] = np.where(
        merged['total_population'] > 0,
        (merged['ujjwala_gas_connections'] / merged['total_population']) * 100.0,
        0.0
    )
    
    # Scheme penetration score (equal-weighted average)
    merged['scheme_penetration_score'] = (
        merged['mgnrega_penetration_pct'] + 
        merged['pmay_penetration_pct'] + 
        merged['ujjwala_penetration_pct']
    ) / 3.0
    
    # Select columns
    cols = [
        'ac_no', 'mgnrega_penetration_pct', 'pmay_completion_rate',
        'pmay_penetration_pct', 'ujjwala_penetration_pct', 'scheme_penetration_score',
        'scheme_data_is_district_estimate'
    ]
    return merged[cols]
