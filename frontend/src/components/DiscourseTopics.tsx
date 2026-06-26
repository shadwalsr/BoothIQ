import React from 'react';
import { ConfidenceBadge } from './ConfidenceBadge';

interface DiscourseTopicsData {
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

interface DiscourseTopicsProps {
  discourseData: DiscourseTopicsData | null;
  metadata: { discourse: string };
}

export const DiscourseTopics: React.FC<DiscourseTopicsProps> = ({
  discourseData,
  metadata,
}) => {
  if (!discourseData) {
    return (
      <div className="discourse-panel glass-panel animate-fade-in">
        <h2>Local News Discourse</h2>
        <div className="no-data-cell">No news discourse data available.</div>
      </div>
    );
  }

  const { discourse_data_sparse, topics } = discourseData;

  // Check if we have at least some data
  const hasData = Object.values(topics).some((val) => val !== null && val > 0);

  // Group topics for sorting and display
  const topicList = [
    { id: 'development', label: 'Development & Infrastructure', val: topics.development, color: 'var(--color-accent)' },
    { id: 'unemployment', label: 'Jobs & Unemployment', val: topics.unemployment, color: '#f87171' },
    { id: 'welfare', label: 'Welfare Schemes & Relief', val: topics.welfare, color: 'var(--success)' },
    { id: 'caste', label: 'Caste Dynamics & Politics', val: topics.caste, color: 'var(--color-secondary)' },
    { id: 'communal', label: 'Communal & Social Harmony', val: topics.communal, color: '#f43f5e' },
    { id: 'inflation', label: 'Inflation & Price Rise', val: topics.inflation, color: '#fbbf24' },
    { id: 'other', label: 'Rallies & Campaign Trails', val: topics.other, color: 'var(--text-muted)' },
  ]
    .filter((t) => t.val !== null)
    .sort((a, b) => (b.val || 0) - (a.val || 0));

  return (
    <div className="discourse-panel glass-panel animate-fade-in">
      <div className="discourse-header">
        <h2>Local News Discourse</h2>
        <ConfidenceBadge type="sparse" active={discourse_data_sparse} />
      </div>

      {!hasData ? (
        <div className="empty-discourse-state">
          <div className="empty-icon">📰</div>
          <h3>Sparse Discourse Analytics</h3>
          <p>
            Local media coverage in this constituency is currently below the analytical threshold. Mainstream media tracking shows limited localized discussion topics. Recommendations will default to regional patterns.
          </p>
        </div>
      ) : (
        <div className="discourse-content">
          <p className="discourse-intro">
            Distribution of campaign discourse topic share in local print and digital media news mentions:
          </p>
          
          <div className="topic-bars-list">
            {topicList.map((topic) => {
              const pct = topic.val || 0;
              return (
                <div key={topic.id} className="topic-bar-item">
                  <div className="topic-info-row">
                    <span className="topic-label">{topic.label}</span>
                    <span className="topic-pct font-number">{pct.toFixed(2)}%</span>
                  </div>
                  <div className="progress-track">
                    <div 
                      className="progress-fill" 
                      style={{ 
                        width: `${pct}%`,
                        backgroundColor: topic.color,
                        boxShadow: `0 0 8px ${topic.color}40`
                      }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="citation">Source: {metadata.discourse}</div>

      <style>{`
        .discourse-panel {
          padding: 1.5rem;
          margin-bottom: 1.5rem;
        }
        .discourse-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        .discourse-header h2 {
          border-bottom: none;
          padding-bottom: 0;
          margin-bottom: 0;
        }
        .discourse-intro {
          font-size: 0.9rem;
          color: var(--text-secondary);
          margin-bottom: 1.5rem;
        }
        .empty-discourse-state {
          text-align: center;
          padding: 3rem 2rem;
          background: rgba(255, 255, 255, 0.01);
          border: 1px dashed rgba(255, 255, 255, 0.08);
          border-radius: var(--radius-md);
          margin-bottom: 1rem;
        }
        .empty-icon {
          font-size: 2.5rem;
          margin-bottom: 1rem;
        }
        .empty-discourse-state h3 {
          color: #fff;
          font-size: 1.1rem;
          margin-bottom: 0.5rem;
        }
        .empty-discourse-state p {
          max-width: 500px;
          margin: 0 auto;
          font-size: 0.85rem;
          color: var(--text-muted);
        }
        .topic-bars-list {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
          margin-bottom: 1rem;
        }
        .topic-bar-item {
          display: flex;
          flex-direction: column;
          gap: 0.35rem;
        }
        .topic-info-row {
          display: flex;
          justify-content: space-between;
          font-size: 0.85rem;
        }
        .topic-label {
          color: var(--text-primary);
          font-weight: 500;
        }
        .topic-pct {
          color: #fff;
          font-weight: 600;
        }
      `}</style>
    </div>
  );
};
