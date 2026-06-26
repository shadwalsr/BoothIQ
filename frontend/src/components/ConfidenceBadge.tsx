import React from 'react';

interface ConfidenceBadgeProps {
  type: 'estimate' | 'sparse';
  active: boolean;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ type, active }) => {
  if (type === 'estimate') {
    return active ? (
      <span className="badge badge-warning" title="Welfare data is calculated at the district level and mapped to this constituency.">
        ⚠️ District Estimate
      </span>
    ) : (
      <span className="badge badge-success" title="Welfare data is reported directly at the constituency level.">
        ✓ Constituency Data
      </span>
    );
  } else {
    return active ? (
      <span className="badge badge-warning" title="Discourse mapping is based on sparse news mentions. Treat with caution.">
        ⚠️ Sparse Media Mentions
      </span>
    ) : (
      <span className="badge badge-success" title="Discourse mapping is based on a robust set of news mentions.">
        ✓ Robust Media Data
      </span>
    );
  }
};
