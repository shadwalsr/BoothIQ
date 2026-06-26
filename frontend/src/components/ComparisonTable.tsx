import React from 'react';

interface ElectionResult {
  winner_name: string;
  winner_party: string;
  margin: number;
  voter_turnout_pct: number;
}

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

interface SchemeExposure {
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

interface DiscourseTopics {
  discourse_data_sparse: boolean;
  topics: {
    inflation: number | null;
    communal: number | null;
    development: number | null;
    welfare: number | null;
    caste: number | null;
    unemployment: number | null;
    other: number | null;
  };
}

interface ClusterAssignment {
  cluster_id: number;
  persona_name: string;
  description: string;
}

interface MessagingRecommendation {
  sensitive_flag: boolean;
  recommendation_text: string;
  example_phrasing: string;
  llm_messaging: string;
}

interface DossierData {
  id: number;
  name: string;
  district: string;
  state: string;
  electoral_history: {
    election_2025: ElectionResult | null;
    election_2020: ElectionResult | null;
  };
  demographics: DemographicsData | null;
  scheme_exposure: SchemeExposure | null;
  nfhs_indicators: any;
  discourse_topics: DiscourseTopics | null;
  cluster_assignment: ClusterAssignment | null;
  messaging_recommendation: MessagingRecommendation | null;
}

interface ComparisonTableProps {
  dossiers: DossierData[];
  onExportCsv: () => void;
}

export const ComparisonTable: React.FC<ComparisonTableProps> = ({
  dossiers,
  onExportCsv,
}) => {
  if (dossiers.length === 0) {
    return (
      <div className="comparison-table-panel glass-panel animate-fade-in text-center-panel">
        <p className="no-data-cell">No constituencies selected for comparison.</p>
      </div>
    );
  }

  const formatPct = (val: number | null | undefined) => {
    if (val === null || val === undefined || isNaN(val)) return '—';
    return `${val.toFixed(2)}%`;
  };

  const formatNum = (val: number | null | undefined) => {
    if (val === null || val === undefined) return '—';
    return val.toLocaleString();
  };

  const renderPartyPill = (party: string | undefined) => {
    if (!party) return '—';
    const partyClass = `party-${party.toLowerCase().replace(/[^a-z0-9]/g, '')}`;
    return <span className={`party-pill ${partyClass}`}>{party}</span>;
  };

  const renderHoldOrFlip = (d: DossierData) => {
    const p2025 = d.electoral_history.election_2025?.winner_party;
    const p2020 = d.electoral_history.election_2020?.winner_party;
    if (!p2025 || !p2020) return '—';
    if (p2025 === p2020) {
      return <span className="badge badge-success font-xs">{p2025} HOLD</span>;
    }
    return <span className="badge badge-danger font-xs">{p2025} FLIP ({p2020})</span>;
  };

  return (
    <div className="comparison-table-panel glass-panel animate-fade-in">
      <div className="comparison-table-header">
        <h3 className="section-title">Constituency Comparison Matrix</h3>
        <button type="button" className="btn-secondary font-xs" onClick={onExportCsv}>
          📥 Export CSV Matrix
        </button>
      </div>

      <div className="table-responsive-wrapper">
        <table className="comparison-grid-table">
          <thead>
            <tr>
              <th className="sticky-col metric-header">Comparison Metrics</th>
              {dossiers.map((d) => (
                <th key={d.id} className="constituency-column-header">
                  <div className="header-ac-id">AC #{d.id}</div>
                  <div className="header-name">{d.name}</div>
                  <div className="header-district">{d.district}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* --- SECTION: GENERAL OVERVIEW --- */}
            <tr className="section-divider-row">
              <td colSpan={dossiers.length + 1}>General Overview</td>
            </tr>
            <tr>
              <td className="sticky-col metric-label">District</td>
              {dossiers.map((d) => (
                <td key={d.id}>{d.district}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Electoral Status</td>
              {dossiers.map((d) => (
                <td key={d.id}>{renderHoldOrFlip(d)}</td>
              ))}
            </tr>

            {/* --- SECTION: 2025 ELECTION --- */}
            <tr className="section-divider-row">
              <td colSpan={dossiers.length + 1}>2025 Assembly Election Results</td>
            </tr>
            <tr>
              <td className="sticky-col metric-label">Winning Candidate</td>
              {dossiers.map((d) => (
                <td key={d.id} className="candidate-cell">{d.electoral_history.election_2025?.winner_name || '—'}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Winning Party</td>
              {dossiers.map((d) => (
                <td key={d.id}>{renderPartyPill(d.electoral_history.election_2025?.winner_party)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Victory Margin</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">
                  {d.electoral_history.election_2025?.margin ? `${formatNum(d.electoral_history.election_2025.margin)} votes` : '—'}
                </td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Voter Turnout</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.electoral_history.election_2025?.voter_turnout_pct)}</td>
              ))}
            </tr>

            {/* --- SECTION: 2020 ELECTION --- */}
            <tr className="section-divider-row">
              <td colSpan={dossiers.length + 1}>2020 Assembly Election Results</td>
            </tr>
            <tr>
              <td className="sticky-col metric-label">Winning Candidate</td>
              {dossiers.map((d) => (
                <td key={d.id} className="candidate-cell">{d.electoral_history.election_2020?.winner_name || '—'}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Winning Party</td>
              {dossiers.map((d) => (
                <td key={d.id}>{renderPartyPill(d.electoral_history.election_2020?.winner_party)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Victory Margin</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">
                  {d.electoral_history.election_2020?.margin ? `${formatNum(d.electoral_history.election_2020.margin)} votes` : '—'}
                </td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Voter Turnout</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.electoral_history.election_2020?.voter_turnout_pct)}</td>
              ))}
            </tr>

            {/* --- SECTION: DEMOGRAPHICS --- */}
            <tr className="section-divider-row">
              <td colSpan={dossiers.length + 1}>Demographic Profiles (Census 2011)</td>
            </tr>
            <tr>
              <td className="sticky-col metric-label">Total Population</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatNum(d.demographics?.total_population)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Literacy Rate</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.demographics?.literacy_rate_pct)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Urban / Rural Ratio</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">
                  {d.demographics ? `${formatPct(d.demographics.urban_ratio_pct)} / ${formatPct(d.demographics.rural_ratio_pct)}` : '—'}
                </td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Scheduled Caste (SC) %</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.demographics?.sc_ratio_pct)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Scheduled Tribe (ST) %</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.demographics?.st_ratio_pct)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Hindu Population %</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.demographics?.hindu_ratio_pct)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Muslim Population %</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.demographics?.muslim_ratio_pct)}</td>
              ))}
            </tr>

            {/* --- SECTION: WELFARE EXPOSURE --- */}
            <tr className="section-divider-row">
              <td colSpan={dossiers.length + 1}>Welfare Scheme Penetration</td>
            </tr>
            <tr>
              <td className="sticky-col metric-label">Composite Footprint Score</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number highlighted-val">
                  {d.scheme_exposure?.scheme_penetration_score ? d.scheme_exposure.scheme_penetration_score.toFixed(2) : '—'}
                </td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">MGNREGA Penetration</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.scheme_exposure?.mgnrega_penetration_pct)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">PMAY Completion Rate</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.scheme_exposure?.pmay_completion_rate)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Ujjwala Penetration</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.scheme_exposure?.ujjwala_penetration_pct)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Welfare Data Confidence</td>
              {dossiers.map((d) => (
                <td key={d.id}>
                  {d.scheme_exposure?.scheme_data_is_district_estimate ? (
                    <span className="text-warning font-xs">⚠️ District Est.</span>
                  ) : (
                    <span className="text-success font-xs">✓ Direct AC</span>
                  )}
                </td>
              ))}
            </tr>

            {/* --- SECTION: NEWS DISCOURSE --- */}
            <tr className="section-divider-row">
              <td colSpan={dossiers.length + 1}>Local News Discourse Topic Shares</td>
            </tr>
            <tr>
              <td className="sticky-col metric-label">Development & Infra %</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.discourse_topics?.topics.development)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Jobs & Unemployment %</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.discourse_topics?.topics.unemployment)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Welfare & Schemes %</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.discourse_topics?.topics.welfare)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Caste Politics %</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.discourse_topics?.topics.caste)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Communal Harmony %</td>
              {dossiers.map((d) => (
                <td key={d.id} className="font-number">{formatPct(d.discourse_topics?.topics.communal)}</td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">News Coverage Quality</td>
              {dossiers.map((d) => (
                <td key={d.id}>
                  {d.discourse_topics?.discourse_data_sparse ? (
                    <span className="text-warning font-xs">⚠️ Sparse</span>
                  ) : (
                    <span className="text-success font-xs">✓ Complete</span>
                  )}
                </td>
              ))}
            </tr>

            {/* --- SECTION: STRATEGIC INSIGHTS --- */}
            <tr className="section-divider-row">
              <td colSpan={dossiers.length + 1}>Strategic Segment & Recommendations</td>
            </tr>
            <tr>
              <td className="sticky-col metric-label">Assigned Segment Persona</td>
              {dossiers.map((d) => (
                <td key={d.id} className="strategy-persona-cell">
                  <strong>{d.cluster_assignment?.persona_name || '—'}</strong>
                </td>
              ))}
            </tr>
            <tr>
              <td className="sticky-col metric-label">Rule-Based Campaign Directive</td>
              {dossiers.map((d) => (
                <td key={d.id} className="directive-cell">
                  <div className="directive-scroll">{d.messaging_recommendation?.recommendation_text || '—'}</div>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      <style>{`
        .comparison-table-panel {
          padding: 1.5rem;
          margin-bottom: 2rem;
          background: linear-gradient(135deg, rgba(22, 26, 43, 0.7) 0%, rgba(13, 16, 27, 0.7) 100%);
        }
        .comparison-table-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.25rem;
        }
        .section-title {
          font-family: var(--font-heading);
          color: #fff;
          font-size: 1.25rem;
        }
        .table-responsive-wrapper {
          width: 100%;
          overflow-x: auto;
          border-radius: var(--radius-md);
          border: 1px solid var(--border-color);
        }
        .comparison-grid-table {
          width: 100%;
          border-collapse: collapse;
          text-align: left;
          table-layout: fixed;
        }
        .comparison-grid-table th, 
        .comparison-grid-table td {
          padding: 0.85rem 1rem;
          border-bottom: 1px solid var(--border-color);
          border-right: 1px solid var(--border-color);
          font-size: 0.85rem;
          vertical-align: middle;
          min-width: 180px;
          word-wrap: break-word;
        }
        .comparison-grid-table th:last-child, 
        .comparison-grid-table td:last-child {
          border-right: none;
        }
        .comparison-grid-table th {
          background: rgba(22, 26, 43, 0.95);
          color: var(--text-secondary);
          font-weight: 600;
        }
        .metric-header {
          min-width: 240px;
          width: 240px;
        }
        .sticky-col {
          position: sticky;
          left: 0;
          z-index: 10;
          background: rgba(18, 20, 31, 0.98);
          border-right: 2px solid var(--border-color) !important;
          min-width: 240px;
          width: 240px;
          color: var(--text-primary);
          font-weight: 500;
        }
        .constituency-column-header {
          text-align: center;
          background: rgba(99, 102, 241, 0.05);
        }
        .header-ac-id {
          font-family: var(--font-heading);
          font-size: 0.75rem;
          color: var(--color-accent);
          font-weight: 700;
        }
        .header-name {
          font-family: var(--font-heading);
          font-size: 1.2rem;
          font-weight: 700;
          color: #fff;
          margin: 0.15rem 0;
        }
        .header-district {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        .section-divider-row td {
          background: rgba(99, 102, 241, 0.12);
          color: #fff;
          font-family: var(--font-heading);
          font-weight: 700;
          font-size: 0.85rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          border-right: none;
          text-align: left !important;
          position: sticky;
          left: 0;
        }
        .metric-label {
          background: rgba(18, 20, 31, 0.98);
          font-weight: 500;
          color: var(--text-secondary);
        }
        .candidate-cell {
          font-weight: 500;
          color: #fff;
        }
        .highlighted-val {
          color: var(--color-accent);
          font-weight: 700;
        }
        .strategy-persona-cell {
          color: var(--color-secondary);
        }
        .directive-cell {
          font-size: 0.8rem;
          color: var(--text-secondary);
          line-height: 1.4;
        }
        .directive-scroll {
          max-height: 80px;
          overflow-y: auto;
          padding-right: 0.25rem;
        }
        .text-center-panel {
          padding: 3rem;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .font-xs {
          font-size: 0.75rem;
        }
      `}</style>
    </div>
  );
};
