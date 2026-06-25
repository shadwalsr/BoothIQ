import os
import json
import glob
import pandas as pd
from pathlib import Path

def load_latest_data(data_dir: str) -> pd.DataFrame:
    """
    Loads and flattens all 15 latest datasets for all 243 constituencies,
    returning a single unified DataFrame.
    """
    base_dir = Path(data_dir) / "raw/latest"
    records = []
    
    if not base_dir.exists():
        print(f"Warning: Directory {base_dir} not found.")
        return pd.DataFrame()
        
    for ac in range(1, 244):
        # We start with the basic ac_no
        row = {'ac_no': ac}
        
        # Helper to load and parse a file for a specific data type
        def get_json_data(dt):
            pattern = os.path.join(base_dir, f"AC{ac:03d}_*_{dt}.jsonl")
            files = glob.glob(pattern)
            if not files:
                return {}
            try:
                with open(files[0], 'r', encoding='utf-8') as f:
                    for line in f:
                        return json.loads(line)
            except Exception as e:
                print(f"Error loading {dt} for AC {ac}: {e}")
            return {}
            
        # 1. Agriculture
        ag_data = get_json_data('agriculture')
        crops = ag_data.get('crops', {})
        row.update({
            'ag_soil_type': crops.get('soil_type'),
            'ag_major_crop_kharif': crops.get('major_crop_kharif'),
            'ag_major_crop_rabi': crops.get('major_crop_rabi'),
            'ag_crop_intensity_pct': crops.get('crop_intensity_pct')
        })
        
        # 2. AMF (Assured Minimum Facilities)
        amf_data = get_json_data('amf')
        amf = amf_data.get('assured_minimum_facilities_pct', {})
        row.update({
            'amf_drinking_water_pct': amf.get('drinking_water'),
            'amf_separate_toilets_for_women_pct': amf.get('separate_toilets_for_women'),
            'amf_electricity_connection_pct': amf.get('electricity_connection'),
            'amf_ramps_for_disabled_pct': amf.get('ramps_for_disabled'),
            'amf_wheelchair_availability_pct': amf.get('wheelchair_availability')
        })
        
        # 3. Candidate Social Footprint (JSONB candidate list)
        csf_data = get_json_data('candidate_social_footprint')
        row.update({
            'candidates_digital_footprint': csf_data.get('candidates_digital_footprint')
        })
        
        # 4. DBT (Direct Benefit Transfer)
        dbt_data = get_json_data('dbt')
        dbt = dbt_data.get('dbt_flows_annual_lakhs_inr', {})
        row.update({
            'dbt_pm_kisan_disbursement_lakhs': dbt.get('pm_kisan_disbursement'),
            'dbt_student_scholarships_lakhs': dbt.get('student_scholarships'),
            'dbt_pension_transfers_lakhs': dbt.get('pension_transfers')
        })
        
        # 5. Dialect
        dia_data = get_json_data('dialect')
        row.update({
            'dialect_zone': dia_data.get('dialect_zone'),
            'preferred_campaign_channel': dia_data.get('preferred_campaign_channel')
        })
        
        # 6. Infrastructure
        infra_data = get_json_data('infrastructure')
        fac = infra_data.get('facilities', {})
        row.update({
            'infra_total_primary_schools': fac.get('total_primary_schools'),
            'infra_secondary_schools': fac.get('secondary_schools'),
            'infra_phc_sub_centers': fac.get('phc_sub_centers'),
            'infra_villages_with_broadband_pct': fac.get('villages_with_broadband_pct')
        })
        
        # 7. Language (Mother tongues JSONB)
        lang_data = get_json_data('language')
        row.update({
            'language_mother_tongues_pct': lang_data.get('mother_tongues_pct')
        })
        
        # 8. Law & Order
        lo_data = get_json_data('law_order')
        inc = lo_data.get('annual_incidents_recorded', {})
        row.update({
            'law_property_disputes_pct': inc.get('property_disputes_pct'),
            'law_petty_thefts': inc.get('petty_thefts'),
            'law_communal_friction_cases': inc.get('communal_friction_cases')
        })
        
        # 9. Livelihoods
        liv_data = get_json_data('livelihoods')
        shg = liv_data.get('jeevika_shgs', {})
        row.update({
            'jeevika_active_shg_groups': shg.get('active_shg_groups'),
            'jeevika_bank_linkages_count': shg.get('bank_linkages_count'),
            'jeevika_total_savings_lakhs': shg.get('total_savings_lakhs_inr'),
            'migration_est_pct': liv_data.get('migration_est_pct')
        })
        
        # 10. Markets
        mkt_data = get_json_data('markets')
        mkt = mkt_data.get('rural_markets', {})
        row.update({
            'markets_registered_mandis_count': mkt.get('registered_mandis_count'),
            'markets_weekly_haats_count': mkt.get('weekly_haats_count'),
            'markets_major_trade_day': mkt.get('major_trade_day')
        })
        
        # 11. MLALAD Funds
        mla_data = get_json_data('mlalad')
        funds = mla_data.get('funds_lakhs_inr', {})
        row.update({
            'mlalad_total_allocated_crores': funds.get('total_allocated_crores'),
            'mlalad_total_spent_crores': funds.get('total_spent_crores'),
            'mlalad_unspent_balance_crores': funds.get('unspent_balance_crores'),
            'mlalad_utilization_rate_pct': funds.get('utilization_rate_pct')
        })
        
        # 12. Panchayat Alignment
        pan_data = get_json_data('panchayat')
        pan = pan_data.get('panchayat_summary', {})
        row.update({
            'panchayat_total': pan.get('total_panchayats'),
            'panchayat_mukhiyas_aligned_nda': pan.get('mukhiyas_aligned_nda'),
            'panchayat_mukhiyas_aligned_grand_alliance': pan.get('mukhiyas_aligned_grand_alliance'),
            'panchayat_mukhiyas_independent': pan.get('mukhiyas_independent')
        })
        
        # 13. Power Grid
        pow_data = get_json_data('power_grid')
        supply = pow_data.get('electricity_supply', {})
        row.update({
            'power_avg_daily_supply_hours_rural': supply.get('avg_daily_supply_hours_rural'),
            'power_avg_daily_supply_hours_urban': supply.get('avg_daily_supply_hours_urban'),
            'power_local_transformers_count': supply.get('local_transformers_count')
        })
        
        # 14. Sensitivity Assessment
        sens_data = get_json_data('sensitivity')
        sens = sens_data.get('sensitivity_assessment', {})
        row.update({
            'sensitivity_risk_level': sens.get('sensitivity_risk_level'),
            'sensitivity_historical_incident_hotspots_count': sens.get('historical_incident_hotspots_count'),
            'sensitivity_primary_tension_vector': sens.get('primary_tension_vector')
        })
        
        # 15. Weather
        wea_data = get_json_data('weather')
        curr = wea_data.get('turnout_day_weather_2025', {})
        hist = wea_data.get('historical_climate_averages_oct_nov', {})
        row.update({
            'weather_temp_celsius': curr.get('temperature_celsius'),
            'weather_humidity_pct': curr.get('humidity_pct'),
            'weather_condition': curr.get('condition'),
            'weather_historical_average_temp_c': hist.get('average_temp_c'),
            'weather_historical_average_rainfall_mm': hist.get('average_rainfall_mm')
        })
        
        records.append(row)
        
    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    base_data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    df = load_latest_data(base_data_dir)
    print(f"Loaded {len(df)} records. Columns: {list(df.columns)}")
