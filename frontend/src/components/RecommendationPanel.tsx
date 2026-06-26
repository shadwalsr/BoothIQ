import React from 'react';

interface MessagingRecommendation {
  theme_welfare: boolean;
  theme_change: boolean;
  theme_urban: boolean;
  theme_inclusive: boolean;
  sensitive_flag: boolean;
  recommendation_text: string;
  example_phrasing: string;
  llm_messaging: string;
}

interface RecommendationPanelProps {
  recommendation: MessagingRecommendation | null;
}

export const RecommendationPanel: React.FC<RecommendationPanelProps> = ({
  recommendation,
}) => {
  if (!recommendation) {
    return (
      <div className="recommendations-panel glass-panel animate-fade-in">
        <h2>Strategic Campaign Messaging</h2>
        <div className="no-data-cell">No messaging recommendations available.</div>
      </div>
    );
  }

  const {
    theme_welfare,
    theme_change,
    theme_urban,
    theme_inclusive,
    sensitive_flag,
    recommendation_text,
    example_phrasing,
    llm_messaging,
  } = recommendation;

  return (
    <div className="recommendations-panel glass-panel animate-fade-in">
      <h2>Campaign Messaging & Strategy</h2>

      {/* Sensitive Landscape Banner */}
      {sensitive_flag && (
        <div className="sensitive-warning-banner animate-fade-in">
          <div className="warning-icon">⚠️</div>
          <div className="warning-text">
            <strong>SENSITIVE LANDSCAPE FLAG ACTIVE:</strong> This constituency presents high minority or SC/ST representation. Strategy must remain strictly inclusive, development-focused, and welfare-driven, completely avoiding polarizing rhetoric.
          </div>
        </div>
      )}

      {/* Theme Badges */}
      <div className="theme-badges-row">
        {theme_welfare && <span className="theme-tag tag-welfare">Welfare Emphasis</span>}
        {theme_change && <span className="theme-tag tag-change">Anti-Incumbency Focus</span>}
        {theme_urban && <span className="theme-tag tag-urban">Urban Aspiration</span>}
        {theme_inclusive && <span className="theme-tag tag-inclusive">Social Justice Focus</span>}
        {!theme_welfare && !theme_change && !theme_urban && !theme_inclusive && (
          <span className="theme-tag tag-general">General Campaign Strategy</span>
        )}
      </div>

      <div className="grid-2 messaging-split-grid">
        {/* Panel 1: Rule-Based Strategy (Traceable) */}
        <div className="strategy-card rule-based-card">
          <div className="card-header-label">
            <span className="engine-icon">⚙️</span> Traceable Strategy Engine
          </div>
          <h3>Standard Campaign Guidelines</h3>
          <p className="recommendation-para">{recommendation_text}</p>
          
          <div className="phrasing-box">
            <div className="box-title">Suggested Phrasing / Slogan</div>
            <p className="phrasing-text"><em>{example_phrasing}</em></p>
          </div>
        </div>

        {/* Panel 2: AI Suggested Nuanced Messaging (LLM) */}
        <div className="strategy-card ai-messaging-card">
          <div className="card-header-label ai-label">
            <span className="engine-icon">✨</span> AI-Suggested Nuanced Messaging
          </div>
          <h3>Contextual AI Synthesis</h3>
          <p className="recommendation-para ai-para">{llm_messaging}</p>
          <div className="ai-disclaimer">
            *Generative AI copywriting; review and align with party press guidelines.
          </div>
        </div>
      </div>
      
      <div className="citation">Source: BoothIQ Campaign Strategy Engine (2025)</div>

      <style>{`
        .recommendations-panel {
          padding: 1.5rem;
          margin-bottom: 1.5rem;
        }
        .sensitive-warning-banner {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.25);
          border-radius: var(--radius-md);
          padding: 1rem 1.25rem;
          display: flex;
          gap: 1rem;
          align-items: center;
          margin-bottom: 1.5rem;
          box-shadow: 0 4px 15px rgba(239, 68, 68, 0.05);
        }
        .warning-icon {
          font-size: 1.5rem;
        }
        .warning-text {
          font-size: 0.85rem;
          color: #fca5a5;
          line-height: 1.5;
        }
        .theme-badges-row {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
          flex-wrap: wrap;
        }
        .theme-tag {
          font-size: 0.75rem;
          font-weight: 600;
          padding: 0.3rem 0.8rem;
          border-radius: var(--radius-full);
          font-family: var(--font-heading);
          text-transform: uppercase;
          letter-spacing: 0.02em;
          border: 1px solid transparent;
        }
        .tag-welfare {
          background: rgba(16, 185, 129, 0.1);
          color: #34d399;
          border-color: rgba(16, 185, 129, 0.2);
        }
        .tag-change {
          background: rgba(245, 158, 11, 0.1);
          color: #fbbf24;
          border-color: rgba(245, 158, 11, 0.2);
        }
        .tag-urban {
          background: rgba(6, 182, 212, 0.1);
          color: #22d3ee;
          border-color: rgba(6, 182, 212, 0.2);
        }
        .tag-inclusive {
          background: rgba(168, 85, 247, 0.1);
          color: #c084fc;
          border-color: rgba(168, 85, 247, 0.2);
        }
        .tag-general {
          background: rgba(255, 255, 255, 0.05);
          color: var(--text-secondary);
          border-color: rgba(255, 255, 255, 0.1);
        }
        
        .strategy-card {
          border-radius: var(--radius-md);
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
          position: relative;
        }
        .rule-based-card {
          background: rgba(255, 255, 255, 0.01);
          border: 1px solid var(--border-color);
        }
        .ai-messaging-card {
          background: linear-gradient(135deg, rgba(168, 85, 247, 0.04) 0%, rgba(99, 102, 241, 0.04) 100%);
          border: 1px solid rgba(168, 85, 247, 0.2);
          box-shadow: 0 4px 20px rgba(168, 85, 247, 0.05);
        }
        .ai-messaging-card:hover {
          border-color: rgba(168, 85, 247, 0.4);
          box-shadow: 0 0 20px rgba(168, 85, 247, 0.15), var(--shadow-lg);
        }
        .card-header-label {
          font-family: var(--font-heading);
          font-size: 0.7rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-secondary);
          display: inline-flex;
          align-items: center;
          gap: 0.35rem;
        }
        .ai-label {
          color: #c084fc;
        }
        .strategy-card h3 {
          font-size: 1.15rem;
          color: #fff;
          margin-bottom: 0.25rem;
        }
        .recommendation-para {
          font-size: 0.9rem;
          line-height: 1.6;
          color: var(--text-secondary);
        }
        .ai-para {
          color: #f1f5f9;
        }
        .phrasing-box {
          background: rgba(255, 255, 255, 0.02);
          border-left: 3px solid var(--color-primary);
          padding: 0.75rem 1rem;
          border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
          margin-top: auto;
        }
        .box-title {
          font-size: 0.65rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-muted);
          margin-bottom: 0.25rem;
        }
        .phrasing-text {
          font-size: 0.9rem;
          color: #fff;
        }
        .ai-disclaimer {
          font-size: 0.7rem;
          color: var(--text-muted);
          font-style: italic;
          margin-top: auto;
        }
      `}</style>
    </div>
  );
};
