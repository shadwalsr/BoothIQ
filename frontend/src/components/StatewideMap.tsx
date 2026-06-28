import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';

interface StatewideMapProps {
  onSelectConstituency: (id: number) => void;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const clusterColors: { [key: number]: string } = {
  0: '#10b981', // Emerald - Welfare-Satisfied Incumbent Strongholds
  1: '#6366f1', // Indigo - Welfare-Exposed Stagnant Seats
  2: '#ef4444', // Rose - Marginalized Minority Belt
  3: '#06b6d4', // Cyan - Rural Campaign-Driven Belts
  4: '#a855f7', // Purple - Aspirational Urban Centers
  5: '#f59e0b', // Amber - High-Volatility Battlegrounds
};

const getClusterColor = (clusterId: any): string => {
  if (clusterId === null || clusterId === undefined) return '#64748b'; // Gray fallback
  return clusterColors[Number(clusterId)] || '#64748b';
};

const clusterPersonas = [
  { id: 0, name: 'Welfare Incumbent Strongholds', color: '#10b981', desc: 'Rural, high-welfare, pro-incumbent seats' },
  { id: 1, name: 'Welfare-Exposed Stagnant', color: '#6366f1', desc: 'Rural, high-welfare, flat-swing/turnout seats' },
  { id: 2, name: 'Marginalized Minority Belt', color: '#ef4444', desc: 'High minority, low-literacy/welfare seats' },
  { id: 3, name: 'Rural Campaign-Driven Belts', color: '#06b6d4', desc: 'Rural, low-welfare, general campaign focus' },
  { id: 4, name: 'Aspirational Urban Centers', color: '#a855f7', desc: 'Highly urban, infrastructure & jobs focus' },
  { id: 5, name: 'High-Volatility Battlegrounds', color: '#f59e0b', desc: 'Rural, high youth unemployment, thin victory margin' },
];

export const StatewideMap: React.FC<StatewideMapProps> = ({
  onSelectConstituency,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    if (mapRef.current) return; // Map already initialized

    let isCancelled = false;

    // 1. Initialize Leaflet Map (Centered on Bihar)
    const map = L.map(containerRef.current, {
      center: [25.75, 85.9],
      zoom: 7.5,
      zoomControl: true,
      minZoom: 6,
      maxZoom: 12,
    });
    mapRef.current = map;

    // 2. Load CartoDB Dark Matter tile layer for glowing dark war-room theme
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 20,
    }).addTo(map);

    // 3. Fetch consolidated GeoJSON boundary data
    const fetchGeoJSON = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/spatial`);
        if (!res.ok) throw new Error('Failed to load spatial constituency map data');
        const data = await res.json();

        if (isCancelled) return;

        // 4. Create GeoJSON Layer
        const geoJsonLayer = L.geoJSON(data, {
          style: (feature) => {
            const cid = feature?.properties?.cluster_id;
            return {
              fillColor: getClusterColor(cid),
              weight: 1.5,
              opacity: 0.8,
              color: '#08090d', // Dark border color
              fillOpacity: 0.65, // More vibrant fill
            };
          },
          onEachFeature: (feature, layer) => {
            const props = feature.properties;
            const marginText = props.margin ? `${Number(props.margin).toLocaleString()} votes` : 'N/A';
            const turnoutText = props.voter_turnout_pct ? `${Number(props.voter_turnout_pct).toFixed(1)}%` : 'N/A';
            const deltaSign = props.turnout_delta && props.turnout_delta >= 0 ? '+' : '';
            const deltaText = props.turnout_delta !== null && props.turnout_delta !== undefined 
              ? ` (${deltaSign}${Number(props.turnout_delta).toFixed(1)}%)` 
              : '';
            const competitivenessText = props.competitiveness_score ? `${Number(props.competitiveness_score).toFixed(1)}%` : 'N/A';
            const welfareText = props.scheme_penetration_score ? `${(Number(props.scheme_penetration_score) * 10).toFixed(1)}/10` : 'N/A';

            // Bind glowing dark glassmorphic tooltip
            layer.bindTooltip(
              `<div class="map-ac-tooltip">
                <div class="tooltip-header">
                  <div class="tooltip-ac-id">AC #${props.ac_no}</div>
                  <div class="tooltip-ac-name">${props.ac_name}</div>
                  <div class="tooltip-ac-district">${props.district} District</div>
                </div>
                
                <div class="tooltip-divider"></div>
                
                <div class="tooltip-section">
                  <div class="tooltip-row">
                    <span class="tooltip-label">Segment:</span>
                    <span class="tooltip-value" style="color: ${getClusterColor(props.cluster_id)}; font-weight: 700;">
                      ${props.persona_name || 'Unassigned'}
                    </span>
                  </div>
                  <div class="tooltip-row">
                    <span class="tooltip-label">Winner (2025):</span>
                    <span class="tooltip-value highlight-value">
                      ${props.winner_name || 'N/A'} <span class="party-badge">${props.winner_party || 'N/A'}</span>
                    </span>
                  </div>
                </div>

                <div class="tooltip-divider"></div>

                <div class="tooltip-grid">
                  <div class="tooltip-grid-item">
                    <div class="grid-label">Victory Margin</div>
                    <div class="grid-value">${marginText}</div>
                  </div>
                  <div class="tooltip-grid-item">
                    <div class="grid-label">Turnout</div>
                    <div class="grid-value">${turnoutText}${deltaText}</div>
                  </div>
                  <div class="tooltip-grid-item">
                    <div class="grid-label">Competitiveness</div>
                    <div class="grid-value">${competitivenessText}</div>
                  </div>
                  <div class="tooltip-grid-item">
                    <div class="grid-label">Welfare Score</div>
                    <div class="grid-value">${welfareText}</div>
                  </div>
                </div>
              </div>`,
              { sticky: true, direction: 'auto', className: 'leaflet-glass-tooltip' }
            );

            // Set up interactions
            layer.on({
              mouseover: (e) => {
                const poly = e.target;
                poly.setStyle({
                  weight: 2.5,
                  color: '#ffffff', // Glow highlight boundary
                  fillOpacity: 0.85,
                });
                poly.bringToFront();
              },
              mouseout: (e) => {
                geoJsonLayer.resetStyle(e.target);
              },
              click: () => {
                // Switch to dossier page on click
                onSelectConstituency(props.ac_no);
              },
            });
          },
        }).addTo(map);

        // Adjust bounds to fit constituencies
        map.fitBounds(geoJsonLayer.getBounds(), { padding: [10, 10] });

      } catch (err: any) {
        if (isCancelled) return;
        console.error(err);
        setError(err.message || 'Error loading map boundaries');
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    fetchGeoJSON();

    // 5. Cleanup on unmount
    return () => {
      isCancelled = true;
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [onSelectConstituency]);

  return (
    <div className="statewide-map-workspace animate-fade-in">
      <h2>Statewide Strategic Cluster Map</h2>
      <p className="map-intro-text">
        Bihar campaign terrain mapped by assembly boundaries. Hover to preview constituencies; click to open their strategic dossiers.
      </p>

      <div className="map-grid-layout">
        {/* Map Container */}
        <div className="map-view-card glass-panel">
          {loading && (
            <div className="map-loading-overlay">
              <span className="spinner large"></span>
              <p>Plotting assembly boundaries...</p>
            </div>
          )}
          {error && (
            <div className="map-error-overlay">
              <span>⚠️</span>
              <p>{error}</p>
            </div>
          )}
          <div ref={containerRef} className="leaflet-map-element" />
        </div>

        {/* Map Legend */}
        <div className="map-legend-card glass-panel">
          <h3>Strategic Personas</h3>
          <div className="legend-list">
            {clusterPersonas.map((persona) => (
              <div key={persona.id} className="legend-item">
                <span className="legend-swatch" style={{ backgroundColor: persona.color }} />
                <div className="legend-details">
                  <div className="legend-persona-name">{persona.name}</div>
                  <div className="legend-persona-desc">{persona.desc}</div>
                </div>
              </div>
            ))}
            <div className="legend-item">
              <span className="legend-swatch" style={{ backgroundColor: '#64748b' }} />
              <div className="legend-details">
                <div className="legend-persona-name">Unassigned</div>
                <div className="legend-persona-desc">Constituencies without segment tagging</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .statewide-map-workspace {
          margin-bottom: 2rem;
        }
        .map-intro-text {
          font-size: 0.9rem;
          color: var(--text-secondary);
          margin-bottom: 1.5rem;
        }
        .map-grid-layout {
          display: grid;
          grid-template-columns: 1fr 300px;
          gap: 1.5rem;
          align-items: start;
        }
        @media (max-width: 1024px) {
          .map-grid-layout {
            grid-template-columns: 1fr;
          }
        }
        .map-view-card {
          position: relative;
          height: 600px;
          padding: 0.5rem;
          border-radius: var(--radius-lg);
          overflow: hidden;
        }
        .leaflet-map-element {
          width: 100%;
          height: 100%;
          border-radius: calc(var(--radius-lg) - 0.5rem);
          z-index: 1;
          background: #08090d;
        }
        .map-loading-overlay,
        .map-error-overlay {
          position: absolute;
          inset: 0;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: rgba(10, 11, 16, 0.85);
          backdrop-filter: blur(8px);
          z-index: 2;
          color: var(--text-secondary);
          gap: 1rem;
        }
        .map-error-overlay p {
          color: #fca5a5;
        }
        .map-legend-card {
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .map-legend-card h3 {
          font-size: 1.1rem;
          color: #fff;
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
          padding-bottom: 0.5rem;
          font-family: var(--font-heading);
        }
        .legend-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .legend-item {
          display: flex;
          gap: 0.75rem;
          align-items: flex-start;
        }
        .legend-swatch {
          display: block;
          width: 14px;
          height: 14px;
          border-radius: 4px;
          flex-shrink: 0;
          margin-top: 0.15rem;
          box-shadow: 0 0 6px rgba(255,255,255,0.05);
        }
        .legend-details {
          display: flex;
          flex-direction: column;
          gap: 0.15rem;
        }
        .legend-persona-name {
          font-size: 0.85rem;
          font-weight: 600;
          color: #fff;
        }
        .legend-persona-desc {
          font-size: 0.7rem;
          color: var(--text-muted);
          line-height: 1.3;
        }

        /* Leaflet custom dark glassmorphic tooltip styles */
        .leaflet-glass-tooltip {
          background: rgba(10, 11, 16, 0.9) !important;
          backdrop-filter: blur(8px) !important;
          -webkit-backdrop-filter: blur(8px) !important;
          border: 1px solid rgba(255, 255, 255, 0.08) !important;
          border-radius: 8px !important;
          padding: 0.75rem !important;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5) !important;
          color: #fff !important;
          font-family: var(--font-sans) !important;
        }
        .leaflet-tooltip-pane .leaflet-glass-tooltip::before {
          border-top-color: rgba(10, 11, 16, 0.9) !important;
        }
        .map-ac-tooltip {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          min-width: 250px;
        }
        .tooltip-header {
          display: flex;
          flex-direction: column;
          gap: 0.1rem;
        }
        .tooltip-ac-id {
          font-family: var(--font-heading);
          font-size: 0.7rem;
          font-weight: 700;
          color: #a855f7;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .tooltip-ac-name {
          font-size: 1.15rem;
          font-weight: 700;
          color: #fff;
          font-family: var(--font-heading);
          margin-bottom: 0.05rem;
        }
        .tooltip-ac-district {
          font-size: 0.75rem;
          color: #94a3b8;
        }
        .tooltip-divider {
          height: 1px;
          background: rgba(255, 255, 255, 0.08);
          margin: 0.4rem 0;
        }
        .tooltip-row {
          display: flex;
          justify-content: space-between;
          font-size: 0.8rem;
          gap: 1rem;
          margin-bottom: 0.25rem;
        }
        .tooltip-label {
          color: #94a3b8;
        }
        .tooltip-value {
          color: #fff;
          text-align: right;
        }
        .highlight-value {
          color: #38bdf8;
          font-weight: 600;
        }
        .party-badge {
          background: rgba(99, 102, 241, 0.2);
          color: #a5b4fc;
          padding: 1px 5px;
          border-radius: 4px;
          font-size: 0.7rem;
          font-weight: 700;
          margin-left: 0.25rem;
          border: 1px solid rgba(165, 180, 252, 0.15);
        }
        .tooltip-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0.5rem;
          margin-top: 0.25rem;
        }
        .tooltip-grid-item {
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.05);
          padding: 0.35rem 0.5rem;
          border-radius: 6px;
        }
        .grid-label {
          font-size: 0.55rem;
          color: #64748b;
          text-transform: uppercase;
          font-weight: 700;
          letter-spacing: 0.02em;
          margin-bottom: 0.1rem;
        }
        .grid-value {
          font-size: 0.8rem;
          font-weight: 600;
          color: #f1f5f9;
        }
      `}</style>
    </div>
  );
};
