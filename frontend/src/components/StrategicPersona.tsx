import React from 'react';

interface ClusterAssignment {
  cluster_id: number;
  persona_name: string;
  description: string;
}

interface MemberConstituency {
  id: number;
  name: string;
  district: string;
}

interface StrategicPersonaProps {
  assignment: ClusterAssignment | null;
  members: MemberConstituency[];
  activeId: number;
  onSelectMember: (id: number) => void;
  loadingMembers: boolean;
}

export const StrategicPersona: React.FC<StrategicPersonaProps> = ({
  assignment,
  members,
  activeId,
  onSelectMember,
  loadingMembers,
}) => {
  if (!assignment) {
    return (
      <div className="persona-panel glass-panel animate-fade-in">
        <h2>Strategic Segment & Persona</h2>
        <div className="no-data-cell">No cluster assignment available.</div>
      </div>
    );
  }

  // Filter out the active constituency itself, and limit to 5 members
  const similarConstituencies = members
    .filter((m) => m.id !== activeId)
    .slice(0, 6);

  return (
    <div className="persona-panel glass-panel animate-fade-in">
      <h2>Strategic Persona Profile</h2>

      <div className="persona-content-grid">
        {/* Persona Card */}
        <div className="persona-detail-card">
          <div className="persona-header-row">
            <span className="cluster-number-tag">Cluster #{assignment.cluster_id}</span>
            <h3 className="persona-name">{assignment.persona_name}</h3>
          </div>
          <p className="persona-description">{assignment.description}</p>
        </div>

        {/* Similar Constituencies */}
        <div className="similar-members-card">
          <h3>Similar Constituencies (Same Segment)</h3>
          {loadingMembers ? (
            <div className="loading-members-state">
              <span className="spinner small"></span> Fetching peers...
            </div>
          ) : similarConstituencies.length === 0 ? (
            <div className="no-similar-state">No other constituencies in this cluster.</div>
          ) : (
            <div className="members-links-grid">
              {similarConstituencies.map((member) => (
                <button
                  key={member.id}
                  type="button"
                  className="member-btn"
                  onClick={() => onSelectMember(member.id)}
                  title={`View Dossier for ${member.name}`}
                >
                  <span className="m-name">{member.name}</span>
                  <span className="m-dist">{member.district}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <style>{`
        .persona-panel {
          padding: 1.5rem;
          margin-bottom: 1.5rem;
        }
        .persona-content-grid {
          display: grid;
          grid-template-columns: 1.2fr 1fr;
          gap: 1.5rem;
          margin-top: 1rem;
        }
        @media (max-width: 1024px) {
          .persona-content-grid {
            grid-template-columns: 1fr;
          }
        }
        .persona-detail-card {
          background: rgba(168, 85, 247, 0.03);
          border: 1px solid rgba(168, 85, 247, 0.15);
          border-radius: var(--radius-md);
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
          box-shadow: 0 4px 20px rgba(168, 85, 247, 0.05);
        }
        .persona-header-row {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        .cluster-number-tag {
          font-family: var(--font-heading);
          font-size: 0.75rem;
          font-weight: 700;
          color: var(--color-secondary);
          text-transform: uppercase;
          letter-spacing: 0.1em;
        }
        .persona-name {
          font-size: 1.4rem;
          color: #fff;
          font-weight: 700;
          margin-bottom: 0;
          border-bottom: none;
          padding-bottom: 0;
        }
        .persona-description {
          font-size: 0.95rem;
          line-height: 1.6;
          color: var(--text-primary);
        }
        
        .similar-members-card {
          background: rgba(255, 255, 255, 0.01);
          border: 1px solid rgba(255, 255, 255, 0.03);
          border-radius: var(--radius-md);
          padding: 1.25rem;
        }
        .similar-members-card h3 {
          font-size: 1rem;
          color: #fff;
          margin-bottom: 1rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
          padding-bottom: 0.5rem;
        }
        .loading-members-state {
          font-size: 0.85rem;
          color: var(--text-muted);
          padding: 1rem 0;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .no-similar-state {
          font-size: 0.85rem;
          color: var(--text-muted);
          padding: 1rem 0;
        }
        .members-links-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 0.5rem;
        }
        @media (max-width: 480px) {
          .members-links-grid {
            grid-template-columns: 1fr;
          }
        }
        .member-btn {
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: var(--radius-sm);
          padding: 0.5rem 0.75rem;
          text-align: left;
          cursor: pointer;
          transition: background var(--transition-fast), border-color var(--transition-fast), transform var(--transition-fast);
          display: flex;
          flex-direction: column;
        }
        .member-btn:hover {
          background: rgba(99, 102, 241, 0.08);
          border-color: rgba(99, 102, 241, 0.3);
          transform: translateY(-1px);
        }
        .member-btn .m-name {
          font-size: 0.85rem;
          font-weight: 500;
          color: #fff;
        }
        .member-btn .m-dist {
          font-size: 0.7rem;
          color: var(--text-secondary);
        }
        .spinner.small {
          width: 0.85rem;
          height: 0.85rem;
          border-width: 1.5px;
        }
      `}</style>
    </div>
  );
};
