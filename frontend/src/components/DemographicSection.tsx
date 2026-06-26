import React from 'react';

interface DemographicsData {
  total_population: number;
  literacy_rate_pct: number;
  urban_ratio_pct: number;
  rural_ratio_pct: number;
  sc_ratio_pct: number;
  st_ratio_pct: number;
  hindu_ratio_pct: number;
  muslim_ratio_pct: number;
}

interface NfhsData {
  children_under_5_years_who_are_stunted_pct: number;
  households_using_improved_sanitation_facility_pct: number;
  households_with_electricity_pct: number;
  households_with_improved_drinking_water_source_pct: number;
  women_who_are_literate_pct: number;
  nfhs_version: string;
}

interface DemographicSectionProps {
  demographics: DemographicsData | null;
  nfhs: NfhsData | null;
  metadata: { demographics: string; nfhs: string };
}

export const DemographicSection: React.FC<DemographicSectionProps> = ({
  demographics,
  nfhs,
  metadata,
}) => {
  if (!demographics) {
    return (
      <div className="demographics-panel glass-panel animate-fade-in">
        <h2>Demographic & Social Profile</h2>
        <div className="no-data-cell">No demographic data available.</div>
      </div>
    );
  }

  return (
    <div className="demographics-panel glass-panel animate-fade-in">
      <h2>Demographics & Health Metrics</h2>

      <div className="grid-2">
        {/* Left Card: Census Demographics */}
        <div className="demo-sub-card">
          <h3>Census Profile (2011)</h3>
          
          <div className="demo-metric-row">
            <div className="metric-item">
              <span className="label">Total Population</span>
              <span className="val font-number">{demographics.total_population.toLocaleString()}</span>
            </div>
            <div className="metric-item">
              <span className="label">Literacy Rate</span>
              <span className="val font-number">{demographics.literacy_rate_pct}%</span>
            </div>
          </div>

          <div className="progress-bar-group">
            <div className="progress-label-row">
              <span>Urban ({demographics.urban_ratio_pct}%)</span>
              <span>Rural ({demographics.rural_ratio_pct}%)</span>
            </div>
            <div className="progress-track">
              <div 
                className="progress-fill fill-accent" 
                style={{ width: `${demographics.urban_ratio_pct}%` }}
              ></div>
            </div>
          </div>

          <div className="progress-bar-group">
            <div className="progress-label-row">
              <span>Hindu ({demographics.hindu_ratio_pct}%)</span>
              <span>Muslim ({demographics.muslim_ratio_pct}%)</span>
            </div>
            <div className="progress-track">
              <div 
                className="progress-fill fill-primary" 
                style={{ width: `${demographics.hindu_ratio_pct}%` }}
              ></div>
            </div>
          </div>

          <div className="progress-bar-group">
            <div className="progress-label-row">
              <span>Scheduled Caste SC ({demographics.sc_ratio_pct}%)</span>
              <span>Scheduled Tribe ST ({demographics.st_ratio_pct}%)</span>
            </div>
            <div className="progress-track">
              <div 
                className="progress-fill fill-secondary" 
                style={{ width: `${demographics.sc_ratio_pct}%` }}
              ></div>
            </div>
          </div>
          
          <div className="citation">Source: {metadata.demographics}</div>
        </div>

        {/* Right Card: Health & Living Standards (NFHS-5) */}
        <div className="demo-sub-card">
          <h3>Health & Infrastructure (NFHS-5)</h3>
          
          {nfhs ? (
            <div className="nfhs-list">
              <div className="nfhs-item">
                <div className="nfhs-info">
                  <span className="nfhs-label">Electricity Access</span>
                  <span className="nfhs-val font-number">{nfhs.households_with_electricity_pct}%</span>
                </div>
                <div className="progress-track small">
                  <div className="progress-fill fill-success" style={{ width: `${nfhs.households_with_electricity_pct}%` }}></div>
                </div>
              </div>

              <div className="nfhs-item">
                <div className="nfhs-info">
                  <span className="nfhs-label">Improved Drinking Water</span>
                  <span className="nfhs-val font-number">{nfhs.households_with_improved_drinking_water_source_pct}%</span>
                </div>
                <div className="progress-track small">
                  <div className="progress-fill fill-success" style={{ width: `${nfhs.households_with_improved_drinking_water_source_pct}%` }}></div>
                </div>
              </div>

              <div className="nfhs-item">
                <div className="nfhs-info">
                  <span className="nfhs-label">Improved Sanitation Facility</span>
                  <span className="nfhs-val font-number">{nfhs.households_using_improved_sanitation_facility_pct}%</span>
                </div>
                <div className="progress-track small">
                  <div className="progress-fill fill-success" style={{ width: `${nfhs.households_using_improved_sanitation_facility_pct}%` }}></div>
                </div>
              </div>

              <div className="nfhs-item">
                <div className="nfhs-info">
                  <span className="nfhs-label">Women Literacy Rate</span>
                  <span className="nfhs-val font-number">{nfhs.women_who_are_literate_pct}%</span>
                </div>
                <div className="progress-track small">
                  <div className="progress-fill fill-success" style={{ width: `${nfhs.women_who_are_literate_pct}%` }}></div>
                </div>
              </div>

              <div className="nfhs-item">
                <div className="nfhs-info">
                  <span className="nfhs-label">Under-5 Children Stunted</span>
                  <span className="nfhs-val font-number warning-text">{nfhs.children_under_5_years_who_are_stunted_pct}%</span>
                </div>
                <div className="progress-track small">
                  <div className="progress-fill fill-warning" style={{ width: `${nfhs.children_under_5_years_who_are_stunted_pct}%` }}></div>
                </div>
              </div>

              <div className="citation">Source: {metadata.nfhs} ({nfhs.nfhs_version})</div>
            </div>
          ) : (
            <div className="no-data-cell">No NFHS health survey data available.</div>
          )}
        </div>
      </div>

      <style>{`
        .demographics-panel {
          padding: 1.5rem;
          margin-bottom: 1.5rem;
        }
        .demo-sub-card {
          background: rgba(255, 255, 255, 0.01);
          border: 1px solid rgba(255, 255, 255, 0.03);
          border-radius: var(--radius-md);
          padding: 1.25rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .demo-sub-card h3 {
          font-size: 1.1rem;
          color: #fff;
          margin-bottom: 0.5rem;
          font-family: var(--font-heading);
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
          padding-bottom: 0.5rem;
        }
        .demo-metric-row {
          display: flex;
          justify-content: space-between;
          gap: 1rem;
          margin-bottom: 0.5rem;
        }
        .metric-item {
          flex: 1;
          display: flex;
          flex-direction: column;
          background: rgba(255, 255, 255, 0.02);
          padding: 0.75rem;
          border-radius: var(--radius-sm);
          border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .metric-item .label {
          font-size: 0.7rem;
          text-transform: uppercase;
          color: var(--text-secondary);
          margin-bottom: 0.25rem;
        }
        .metric-item .val {
          font-size: 1.3rem;
          font-weight: 700;
          color: #fff;
        }
        .progress-bar-group {
          display: flex;
          flex-direction: column;
          gap: 0.35rem;
        }
        .progress-label-row {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
          color: var(--text-secondary);
        }
        .progress-track {
          height: 8px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: var(--radius-full);
          overflow: hidden;
          position: relative;
        }
        .progress-track.small {
          height: 6px;
        }
        .progress-fill {
          height: 100%;
          border-radius: var(--radius-full);
        }
        .fill-accent { background: var(--color-accent); }
        .fill-primary { background: var(--color-primary); }
        .fill-secondary { background: var(--color-secondary); }
        .fill-success { background: var(--success); }
        .fill-warning { background: var(--warning); }
        
        .nfhs-list {
          display: flex;
          flex-direction: column;
          gap: 0.85rem;
        }
        .nfhs-item {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        .nfhs-info {
          display: flex;
          justify-content: space-between;
          font-size: 0.85rem;
        }
        .nfhs-label {
          color: var(--text-secondary);
        }
        .nfhs-val {
          color: #fff;
          font-weight: 600;
        }
        .warning-text {
          color: var(--warning);
        }
      `}</style>
    </div>
  );
};
