import React from 'react';

interface ElectionResult {
  winner_name: string;
  winner_party: string;
  margin: number;
  voter_turnout_pct: number;
  votes_polled?: number;
}

interface ElectoralHistoryProps {
  election2025: ElectionResult | null;
  election2020: ElectionResult | null;
  metadata: { electoral: string };
}

export const ElectoralHistory: React.FC<ElectoralHistoryProps> = ({
  election2025,
  election2020,
  metadata,
}) => {
  return (
    <div className="electoral-history-panel glass-panel animate-fade-in">
      <h2>Electoral History & Trends</h2>
      
      <div className="table-responsive">
        <table className="dossier-table">
          <thead>
            <tr>
              <th>Year</th>
              <th>Winner Candidate</th>
              <th>Party</th>
              <th>Margin of Victory</th>
              <th>Voter Turnout</th>
            </tr>
          </thead>
          <tbody>
            {election2025 && (
              <tr className="current-year-row">
                <td>
                  <span className="year-badge current">2025</span>
                </td>
                <td className="candidate-cell">{election2025.winner_name}</td>
                <td>
                  <span className={`party-pill party-${election2025.winner_party.toLowerCase().replace(/[^a-z0-9]/g, '')}`}>
                    {election2025.winner_party}
                  </span>
                </td>
                <td className="numeric-cell font-number">
                  {election2025.margin ? election2025.margin.toLocaleString() : 'N/A'} votes
                </td>
                <td className="numeric-cell font-number">
                  {election2025.voter_turnout_pct ? `${election2025.voter_turnout_pct}%` : 'N/A'}
                </td>
              </tr>
            )}
            {election2020 && (
              <tr>
                <td>
                  <span className="year-badge">2020</span>
                </td>
                <td className="candidate-cell">{election2020.winner_name}</td>
                <td>
                  <span className={`party-pill party-${election2020.winner_party.toLowerCase().replace(/[^a-z0-9]/g, '')}`}>
                    {election2020.winner_party}
                  </span>
                </td>
                <td className="numeric-cell font-number">
                  {election2020.margin ? election2020.margin.toLocaleString() : 'N/A'} votes
                </td>
                <td className="numeric-cell font-number">
                  {election2020.voter_turnout_pct ? `${election2020.voter_turnout_pct}%` : 'N/A'}
                </td>
              </tr>
            )}
            {!election2025 && !election2020 && (
              <tr>
                <td colSpan={5} className="no-data-cell">No electoral history data found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="citation">Source: {metadata.electoral}</div>

      <style>{`
        .electoral-history-panel {
          padding: 1.5rem;
          margin-bottom: 1.5rem;
        }
        .table-responsive {
          width: 100%;
          overflow-x: auto;
          margin-top: 1rem;
        }
        .dossier-table {
          width: 100%;
          border-collapse: collapse;
          text-align: left;
        }
        .dossier-table th {
          padding: 0.75rem 1rem;
          font-family: var(--font-heading);
          font-size: 0.8rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-secondary);
          border-bottom: 2px solid var(--border-color);
        }
        .dossier-table td {
          padding: 1rem;
          font-size: 0.9rem;
          border-bottom: 1px solid var(--border-color);
          color: var(--text-primary);
        }
        .current-year-row {
          background: rgba(99, 102, 241, 0.03);
        }
        .year-badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: var(--radius-sm);
          font-size: 0.75rem;
          font-weight: 700;
          font-family: var(--font-heading);
          background: rgba(255, 255, 255, 0.05);
          color: var(--text-secondary);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .year-badge.current {
          background: rgba(99, 102, 241, 0.2);
          color: var(--color-primary);
          border-color: rgba(99, 102, 241, 0.4);
        }
        .candidate-cell {
          font-weight: 500;
        }
        .party-pill {
          display: inline-block;
          padding: 0.2rem 0.6rem;
          border-radius: var(--radius-full);
          font-size: 0.75rem;
          font-weight: 600;
          letter-spacing: 0.02em;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        /* Specific Party Styling if available */
        .party-rjd {
          background: rgba(16, 185, 129, 0.15);
          color: #34d399;
          border-color: rgba(16, 185, 129, 0.3);
        }
        .party-jdu {
          background: rgba(59, 130, 246, 0.15);
          color: #60a5fa;
          border-color: rgba(59, 130, 246, 0.3);
        }
        .party-bjp {
          background: rgba(245, 158, 11, 0.15);
          color: #fbbf24;
          border-color: rgba(245, 158, 11, 0.3);
        }
        .party-inc {
          background: rgba(239, 68, 68, 0.15);
          color: #f87171;
          border-color: rgba(239, 68, 68, 0.3);
        }
        .numeric-cell {
          text-align: left;
        }
        .font-number {
          font-family: var(--font-heading);
          font-weight: 500;
        }
        .no-data-cell {
          text-align: center;
          color: var(--text-muted);
          padding: 2rem;
        }
      `}</style>
    </div>
  );
};
