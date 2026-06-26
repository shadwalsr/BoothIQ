import React from 'react';
import { ConfidenceBadge } from './ConfidenceBadge';

interface SchemeData {
  mgnrega_active_job_cards: number | null;
  mgnrega_expenditure_lakhs: number | null;
  pmay_homes_sanctioned: number | null;
  pmay_homes_completed: number | null;
  ujjwala_gas_connections: number | null;
  mgnrega_penetration_pct: number | null;
  pmay_completion_rate: number | null;
  pmay_penetration_pct: number | null;
  ujjwala_penetration_pct: number | null;
  scheme_penetration_score: number | null;
  scheme_data_is_district_estimate: boolean;
}

interface WelfareExposureProps {
  schemeData: SchemeData | null;
  metadata: { welfare: string };
}

export const WelfareExposure: React.FC<WelfareExposureProps> = ({
  schemeData,
  metadata,
}) => {
  if (!schemeData) {
    return (
      <div className="welfare-panel glass-panel animate-fade-in">
        <h2>Welfare Scheme Exposure</h2>
        <div className="no-data-cell">No welfare scheme data available.</div>
      </div>
    );
  }

  const formatPct = (val: number | null) => {
    if (val === null || isNaN(val)) return 'N/A';
    return `${val.toFixed(2)}%`;
  };

  const formatNum = (val: number | null) => {
    if (val === null) return 'N/A';
    return val.toLocaleString();
  };

  return (
    <div className="welfare-panel glass-panel animate-fade-in">
      <div className="welfare-header">
        <h2>Welfare Scheme Exposure</h2>
        <ConfidenceBadge 
          type="estimate" 
          active={schemeData.scheme_data_is_district_estimate} 
        />
      </div>

      <div className="welfare-layout">
        {/* Circle composite score */}
        <div className="composite-score-card">
          <div className="radial-score">
            <span className="score-val">
              {schemeData.scheme_penetration_score ? schemeData.scheme_penetration_score.toFixed(1) : 'N/A'}
            </span>
            <span className="score-lbl">Composite Score</span>
          </div>
          <p className="score-desc">
            Calculated score representing the relative welfare delivery footprint in this constituency. Higher scores represent deeper penetration.
          </p>
        </div>

        {/* Detailed cards list */}
        <div className="schemes-detail-list">
          {/* MGNREGA */}
          <div className="scheme-row-card">
            <div className="scheme-meta">
              <h4>MGNREGA Rural Employment</h4>
              <div className="scheme-raw-stats">
                <span>Active Cards: <strong>{formatNum(schemeData.mgnrega_active_job_cards)}</strong></span>
                {schemeData.mgnrega_expenditure_lakhs !== null && (
                  <span>Expenditure: <strong>₹{formatNum(schemeData.mgnrega_expenditure_lakhs)} L</strong></span>
                )}
              </div>
            </div>
            <div className="scheme-penetration">
              <div className="p-title">Penetration Rate</div>
              <div className="p-val font-number">{formatPct(schemeData.mgnrega_penetration_pct)}</div>
            </div>
          </div>

          {/* PMAY */}
          <div className="scheme-row-card">
            <div className="scheme-meta">
              <h4>PMAY (Housing)</h4>
              <div className="scheme-raw-stats">
                {schemeData.pmay_homes_sanctioned !== null ? (
                  <span>Sanctioned: <strong>{formatNum(schemeData.pmay_homes_sanctioned)}</strong></span>
                ) : null}
                {schemeData.pmay_homes_completed !== null ? (
                  <span>Completed: <strong>{formatNum(schemeData.pmay_homes_completed)}</strong></span>
                ) : null}
                {schemeData.pmay_completion_rate !== null && (
                  <span>Completion Rate: <strong>{formatPct(schemeData.pmay_completion_rate)}</strong></span>
                )}
              </div>
            </div>
            <div className="scheme-penetration">
              <div className="p-title">Penetration Rate</div>
              <div className="p-val font-number">{formatPct(schemeData.pmay_penetration_pct)}</div>
            </div>
          </div>

          {/* Ujjwala */}
          <div className="scheme-row-card">
            <div className="scheme-meta">
              <h4>Pradhan Mantri Ujjwala Yojana</h4>
              <div className="scheme-raw-stats">
                <span>Gas Connections: <strong>{formatNum(schemeData.ujjwala_gas_connections)}</strong></span>
              </div>
            </div>
            <div className="scheme-penetration">
              <div className="p-title">Penetration Rate</div>
              <div className="p-val font-number">{formatPct(schemeData.ujjwala_penetration_pct)}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="citation">Source: {metadata.welfare}</div>

      <style>{`
        .welfare-panel {
          padding: 1.5rem;
          margin-bottom: 1.5rem;
        }
        .welfare-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        .welfare-header h2 {
          border-bottom: none;
          padding-bottom: 0;
          margin-bottom: 0;
        }
        .welfare-layout {
          display: grid;
          grid-template-columns: 280px 1fr;
          gap: 1.5rem;
          margin-bottom: 1rem;
        }
        @media (max-width: 768px) {
          .welfare-layout {
            grid-template-columns: 1fr;
          }
        }
        .composite-score-card {
          background: rgba(255, 255, 255, 0.01);
          border: 1px solid rgba(255, 255, 255, 0.03);
          border-radius: var(--radius-md);
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
        }
        .radial-score {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, rgba(99,102,241,0) 70%);
          border: 4px solid var(--color-primary);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          margin-bottom: 1rem;
          box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
        }
        .score-val {
          font-family: var(--font-heading);
          font-size: 2.2rem;
          font-weight: 800;
          color: #fff;
          line-height: 1;
        }
        .score-lbl {
          font-size: 0.65rem;
          text-transform: uppercase;
          color: var(--text-secondary);
          margin-top: 0.25rem;
          letter-spacing: 0.05em;
        }
        .score-desc {
          font-size: 0.75rem;
          color: var(--text-muted);
          line-height: 1.4;
        }
        .schemes-detail-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        .scheme-row-card {
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: var(--radius-md);
          padding: 1rem 1.25rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          transition: background var(--transition-fast), border-color var(--transition-fast);
        }
        .scheme-row-card:hover {
          background: rgba(255, 255, 255, 0.04);
          border-color: rgba(99, 102, 241, 0.25);
        }
        .scheme-meta {
          display: flex;
          flex-direction: column;
          gap: 0.35rem;
        }
        .scheme-meta h4 {
          font-size: 0.95rem;
          color: #fff;
        }
        .scheme-raw-stats {
          display: flex;
          gap: 1rem;
          font-size: 0.75rem;
          color: var(--text-secondary);
          flex-wrap: wrap;
        }
        .scheme-raw-stats strong {
          color: #fff;
        }
        .scheme-penetration {
          text-align: right;
        }
        .p-title {
          font-size: 0.65rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .p-val {
          font-size: 1.4rem;
          font-weight: 700;
          color: var(--color-accent);
        }
      `}</style>
    </div>
  );
};
