import React from 'react';

interface ElectionResult {
  winner_name: string;
  winner_party: string;
  margin: number;
  voter_turnout_pct: number;
  votes_polled?: number;
}

interface DossierHeaderProps {
  id: number;
  name: string;
  district: string;
  state: string;
  election2025: ElectionResult | null;
  election2020: ElectionResult | null;
  metadata: { electoral: string };
  onExport: () => void;
  exportLoading: boolean;
}

export const DossierHeader: React.FC<DossierHeaderProps> = ({
  id,
  name,
  district,
  state,
  election2025,
  election2020,
  metadata,
  onExport,
  exportLoading,
}) => {
  const getHoldOrFlip = () => {
    if (!election2025 || !election2020) return null;
    const p2025 = election2025.winner_party;
    const p2020 = election2020.winner_party;
    if (p2025 === p2020) {
      return {
        type: 'hold',
        text: `${p2025} HOLD`,
        class: 'badge-success',
      };
    } else {
      return {
        type: 'flip',
        text: `${p2025} FLIP from ${p2020}`,
        class: 'badge-danger',
      };
    }
  };

  const status = getHoldOrFlip();

  return (
    <div className="dossier-header-panel glass-panel animate-fade-in">
      <div className="header-top">
        <div>
          <div className="ac-meta">
            Assembly Constituency #{id} • {state}
          </div>
          <h1 className="ac-title">{name}</h1>
          <div className="district-tag">District: {district}</div>
        </div>
        <div className="header-actions">
          {status && <span className={`badge ${status.class} status-badge`}>{status.text}</span>}
          <button 
            type="button" 
            className="btn-primary" 
            onClick={onExport} 
            disabled={exportLoading}
          >
            {exportLoading ? (
              <>
                <span className="spinner"></span> Generating Briefing...
              </>
            ) : (
              <>
                <span>📄</span> Export PDF Dossier
              </>
            )}
          </button>
        </div>
      </div>

      <div className="header-stats-grid">
        <div className="stat-card">
          <div className="stat-label">2025 Winner</div>
          <div className="stat-value">{election2025?.winner_name || 'N/A'}</div>
          <div className="stat-sub">{election2025?.winner_party || 'N/A'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Margin of Victory</div>
          <div className="stat-value">
            {election2025?.margin ? election2025.margin.toLocaleString() : 'N/A'}
          </div>
          <div className="stat-sub">Votes</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Turnout Rate</div>
          <div className="stat-value">{election2025?.voter_turnout_pct ? `${election2025.voter_turnout_pct}%` : 'N/A'}</div>
          <div className="stat-sub">
            vs {election2020?.voter_turnout_pct ? `${election2020.voter_turnout_pct}%` : 'N/A'} in 2020
          </div>
        </div>
      </div>
      
      <div className="citation">Source: {metadata.electoral}</div>

      <style>{`
        .dossier-header-panel {
          padding: 2rem;
          margin-bottom: 1.5rem;
          background: linear-gradient(135deg, rgba(22, 26, 43, 0.7) 0%, rgba(13, 16, 27, 0.7) 100%);
        }
        .header-top {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          border-bottom: 1px solid var(--border-color);
          padding-bottom: 1.5rem;
          margin-bottom: 1.5rem;
          flex-wrap: wrap;
          gap: 1rem;
        }
        .ac-meta {
          font-family: var(--font-heading);
          font-size: 0.85rem;
          color: var(--color-accent);
          text-transform: uppercase;
          letter-spacing: 0.1em;
          margin-bottom: 0.25rem;
        }
        .ac-title {
          font-family: var(--font-heading);
          font-size: 2.5rem;
          font-weight: 800;
          color: #fff;
          line-height: 1.1;
        }
        .district-tag {
          font-size: 0.95rem;
          color: var(--text-secondary);
          margin-top: 0.25rem;
        }
        .header-actions {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex-wrap: wrap;
        }
        .status-badge {
          font-size: 0.85rem;
          padding: 0.4rem 0.9rem;
        }
        .header-stats-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1.5rem;
        }
        @media (max-width: 768px) {
          .header-stats-grid {
            grid-template-columns: 1fr;
          }
          .header-top {
            flex-direction: column;
            align-items: stretch;
          }
          .header-actions {
            justify-content: flex-start;
            flex-direction: row-reverse;
          }
        }
        .stat-card {
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: var(--radius-md);
          padding: 1.25rem;
          transition: background var(--transition-fast), border-color var(--transition-fast);
        }
        .stat-card:hover {
          background: rgba(255, 255, 255, 0.04);
          border-color: rgba(255, 255, 255, 0.1);
        }
        .stat-label {
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-secondary);
          margin-bottom: 0.5rem;
          font-family: var(--font-heading);
        }
        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: #fff;
          font-family: var(--font-heading);
        }
        .stat-sub {
          font-size: 0.8rem;
          color: var(--text-muted);
          margin-top: 0.25rem;
        }
        .spinner {
          display: inline-block;
          width: 1rem;
          height: 1rem;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          border-top-color: #fff;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
