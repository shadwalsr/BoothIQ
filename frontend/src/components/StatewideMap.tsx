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

// Custom 3D Projection Canvas Component
interface Map3DCanvasProps {
  features: any[];
  metric: 'turnout' | 'competitiveness' | 'welfare';
  onSelectConstituency: (id: number) => void;
}

const Map3DCanvas: React.FC<Map3DCanvasProps> = ({
  features,
  metric,
  onSelectConstituency,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [yaw, setYaw] = useState<number>(-0.5); // Horizontal rotation
  const [pitch, setPitch] = useState<number>(0.7); // Vertical tilt
  const [zoom, setZoom] = useState<number>(1.1);
  const [hoveredFeature, setHoveredFeature] = useState<any>(null);
  const dragRef = useRef({ isDragging: false, startX: 0, startY: 0, startYaw: 0, startPitch: 0 });

  // Find bounds of all constituencies
  const bounds = React.useMemo(() => {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    features.forEach((f) => {
      const geom = f.geometry;
      if (!geom || geom.type !== 'Polygon') return;
      const coords = geom.coordinates[0];
      coords.forEach((pt: any) => {
        const [lon, lat] = pt;
        if (lon < minX) minX = lon;
        if (lon > maxX) maxX = lon;
        if (lat < minY) minY = lat;
        if (lat > maxY) maxY = lat;
      });
    });
    return { minX, maxX, minY, maxY, rangeX: maxX - minX, rangeY: maxY - minY };
  }, [features]);

  // Map coordinates
  const getXY = React.useCallback(
    (lon: number, lat: number) => {
      const x = ((lon - bounds.minX) / bounds.rangeX - 0.5) * 360;
      const y = ((lat - bounds.minY) / bounds.rangeY - 0.5) * 360;
      return { x, y: -y };
    },
    [bounds]
  );

  const getPillarHeight = React.useCallback(
    (f: any) => {
      const props = f.properties;
      if (metric === 'turnout') {
        return (props.voter_turnout_pct || 50) * 1.5;
      } else if (metric === 'competitiveness') {
        return (props.competitiveness_score || 50) * 1.5;
      } else if (metric === 'welfare') {
        return (props.scheme_penetration_score || 0) * 15;
      }
      return 50;
    },
    [metric]
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Draw background grid lines (futuristic hologram style)
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    ctx.strokeStyle = 'rgba(99, 102, 241, 0.04)';
    ctx.lineWidth = 1;
    const gridSize = 35;
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    const cosYaw = Math.cos(yaw);
    const sinYaw = Math.sin(yaw);
    const cosPitch = Math.cos(pitch);
    const sinPitch = Math.sin(pitch);
    const centerX = width / 2;
    const centerY = height / 2 + 60; // Offset down slightly

    const project = (x3d: number, y3d: number, z3d: number) => {
      const xRot = x3d * cosYaw - y3d * sinYaw;
      const yRot = x3d * sinYaw + y3d * cosYaw;
      const screenX = centerX + xRot * zoom;
      const screenY = centerY + (yRot * cosPitch - z3d * sinPitch) * zoom;
      return { x: screenX, y: screenY, depth: yRot };
    };

    const pillars = features
      .map((f) => {
        const geom = f.geometry;
        if (!geom || geom.type !== 'Polygon') return null;
        const coords = geom.coordinates[0];
        let sumLon = 0, sumLat = 0;
        coords.forEach((pt: any) => {
          sumLon += pt[0];
          sumLat += pt[1];
        });
        const centroidLon = sumLon / coords.length;
        const centroidLat = sumLat / coords.length;
        const localCoords = getXY(centroidLon, centroidLat);
        const h = getPillarHeight(f);
        const proj = project(localCoords.x, localCoords.y, 0);

        return {
          feature: f,
          x: localCoords.x,
          y: localCoords.y,
          height: h,
          depth: proj.depth,
          hexagonCoords: coords.map((pt: any) => getXY(pt[0], pt[1])),
        };
      })
      .filter(Boolean) as any[];

    // Sort back-to-front
    pillars.sort((a, b) => a.depth - b.depth);

    // Draw pillars
    pillars.forEach((p) => {
      const baseColor = getClusterColor(p.feature.properties.cluster_id);
      const isHovered = hoveredFeature && hoveredFeature.properties.ac_no === p.feature.properties.ac_no;

      const topPts = p.hexagonCoords.map((pt: any) => project(pt.x, pt.y, p.height));
      const basePts = p.hexagonCoords.map((pt: any) => project(pt.x, pt.y, 0));

      // Draw sides
      const n = topPts.length;
      for (let i = 0; i < n - 1; i++) {
        const nextIdx = i + 1;
        const p1Top = topPts[i];
        const p2Top = topPts[nextIdx];
        const p1Base = basePts[i];
        const p2Base = basePts[nextIdx];

        // Backface culling
        const cp = (p2Top.x - p1Top.x) * (p1Base.y - p1Top.y) - (p2Top.y - p1Top.y) * (p1Base.x - p1Top.x);
        if (cp > 0) {
          ctx.beginPath();
          ctx.moveTo(p1Top.x, p1Top.y);
          ctx.lineTo(p2Top.x, p2Top.y);
          ctx.lineTo(p2Base.x, p2Base.y);
          ctx.lineTo(p1Base.x, p1Base.y);
          ctx.closePath();

          const shadingFactor = 0.35 + 0.3 * Math.abs((i / (n - 1)) * 2 - 1);
          ctx.fillStyle = isHovered 
            ? `rgba(255, 255, 255, ${shadingFactor + 0.2})` 
            : adjustColorOpacity(baseColor, shadingFactor);
          ctx.strokeStyle = 'rgba(8, 9, 13, 0.4)';
          ctx.lineWidth = 0.5;
          ctx.fill();
          ctx.stroke();
        }
      }

      // Draw Top Face
      ctx.beginPath();
      ctx.moveTo(topPts[0].x, topPts[0].y);
      for (let i = 1; i < topPts.length; i++) {
        ctx.lineTo(topPts[i].x, topPts[i].y);
      }
      ctx.closePath();

      ctx.fillStyle = isHovered 
        ? 'rgba(255, 255, 255, 0.95)' 
        : adjustColorOpacity(baseColor, 0.75);
      ctx.strokeStyle = isHovered ? '#ffffff' : 'rgba(255, 255, 255, 0.2)';
      ctx.lineWidth = isHovered ? 1.5 : 0.5;
      ctx.fill();
      ctx.stroke();
    });

    function adjustColorOpacity(hex: string, opacity: number): string {
      hex = hex.replace('#', '');
      const r = parseInt(hex.substring(0, 2), 16);
      const g = parseInt(hex.substring(2, 4), 16);
      const b = parseInt(hex.substring(4, 6), 16);
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }

  }, [features, yaw, pitch, zoom, getXY, getPillarHeight, hoveredFeature]);

  const handleMouseDown = (e: React.MouseEvent) => {
    dragRef.current = {
      isDragging: true,
      startX: e.clientX,
      startY: e.clientY,
      startYaw: yaw,
      startPitch: pitch,
    };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    const drag = dragRef.current;
    if (drag.isDragging) {
      const deltaX = e.clientX - drag.startX;
      const deltaY = e.clientY - drag.startY;
      setYaw(drag.startYaw - deltaX * 0.007);
      setPitch(Math.max(0.15, Math.min(1.4, drag.startPitch + deltaY * 0.007)));
    } else {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      const cosYaw = Math.cos(yaw);
      const sinYaw = Math.sin(yaw);
      const cosPitch = Math.cos(pitch);
      const sinPitch = Math.sin(pitch);
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2 + 60;

      let closestF: any = null;
      let minDistance = 18;

      features.forEach((f) => {
        const geom = f.geometry;
        if (!geom || geom.type !== 'Polygon') return;
        const coords = geom.coordinates[0];
        let sumLon = 0, sumLat = 0;
        coords.forEach((pt: any) => {
          sumLon += pt[0];
          sumLat += pt[1];
        });
        const cLon = sumLon / coords.length;
        const cLat = sumLat / coords.length;
        const local = getXY(cLon, cLat);
        const h = getPillarHeight(f);

        const xRot = local.x * cosYaw - local.y * sinYaw;
        const yRot = local.x * sinYaw + local.y * cosYaw;
        const screenX = centerX + xRot * zoom;
        const screenY = centerY + (yRot * cosPitch - h * sinPitch) * zoom;

        const dist = Math.sqrt((screenX - mouseX) ** 2 + (screenY - mouseY) ** 2);
        if (dist < minDistance) {
          minDistance = dist;
          closestF = f;
        }
      });

      setHoveredFeature(closestF);
    }
  };

  const handleMouseUp = () => {
    dragRef.current.isDragging = false;
  };

  const handleWheel = (e: React.WheelEvent) => {
    setZoom((prev) => Math.max(0.5, Math.min(2.5, prev - e.deltaY * 0.0015)));
  };

  const handleCanvasClick = () => {
    if (hoveredFeature) {
      onSelectConstituency(hoveredFeature.properties.ac_no);
    }
  };

  return (
    <div className="canvas-container-3d">
      <canvas
        ref={canvasRef}
        width={750}
        height={500}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        onClick={handleCanvasClick}
        style={{ cursor: dragRef.current.isDragging ? 'grabbing' : hoveredFeature ? 'pointer' : 'grab' }}
      />
      {hoveredFeature && (
        <div className="dossier-hover-panel glass-panel animate-fade-in">
          <div className="hover-ac-no">AC #{hoveredFeature.properties.ac_no}</div>
          <div className="hover-ac-name">{hoveredFeature.properties.ac_name}</div>
          <div className="hover-ac-district">{hoveredFeature.properties.district} District</div>
          <div className="hover-ac-persona" style={{ color: getClusterColor(hoveredFeature.properties.cluster_id) }}>
            {hoveredFeature.properties.persona_name}
          </div>
          <div className="hover-divider" />
          <div className="hover-stat">
            <span className="stat-lbl">Winner (2025):</span>
            <span className="stat-val font-semibold">{hoveredFeature.properties.winner_name} ({hoveredFeature.properties.winner_party})</span>
          </div>
          <div className="hover-stat">
            <span className="stat-lbl">Margin:</span>
            <span className="stat-val">{hoveredFeature.properties.margin ? Number(hoveredFeature.properties.margin).toLocaleString() + ' votes' : 'N/A'}</span>
          </div>
          <div className="hover-stat">
            <span className="stat-lbl">Turnout:</span>
            <span className="stat-val">
              {hoveredFeature.properties.voter_turnout_pct ? Number(hoveredFeature.properties.voter_turnout_pct).toFixed(1) + '%' : 'N/A'}
            </span>
          </div>
          <div className="hover-stat">
            <span className="stat-lbl">Welfare Score:</span>
            <span className="stat-val">
              {hoveredFeature.properties.scheme_penetration_score ? (Number(hoveredFeature.properties.scheme_penetration_score) * 10).toFixed(1) + '/10' : 'N/A'}
            </span>
          </div>
          <div className="hover-click-tip">Click pillar to view dossier</div>
        </div>
      )}
    </div>
  );
};

export const StatewideMap: React.FC<StatewideMapProps> = ({
  onSelectConstituency,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const [viewMode, setViewMode] = useState<'2d' | '3d'>('2d');
  const [metric3D, setMetric3D] = useState<'turnout' | 'competitiveness' | 'welfare'>('turnout');
  const [spatialData, setSpatialData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch consolidated GeoJSON boundary data
  useEffect(() => {
    let isCancelled = false;
    const fetchGeoJSON = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/spatial`);
        if (!res.ok) throw new Error('Failed to load spatial constituency map data');
        const data = await res.json();

        if (isCancelled) return;
        setSpatialData(data);
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
    return () => {
      isCancelled = true;
    };
  }, []);

  // 2D Leaflet initialization
  useEffect(() => {
    if (viewMode !== '2d' || !spatialData || !containerRef.current) return;
    if (mapRef.current) return; // Already initialized

    // Initialize Leaflet Map (Centered on Bihar)
    const map = L.map(containerRef.current, {
      center: [25.75, 85.9],
      zoom: 7.5,
      zoomControl: true,
      minZoom: 6,
      maxZoom: 12,
    });
    mapRef.current = map;

    // Isolate Bihar map: No background tileLayer is added.
    // This removes external borders/states (Nepal, UP, West Bengal, Jharkhand) completely.
    const geoJsonLayer = L.geoJSON(spatialData, {
      style: (feature) => {
        const cid = feature?.properties?.cluster_id;
        return {
          fillColor: getClusterColor(cid),
          weight: 1.5,
          opacity: 0.8,
          color: '#08090d',
          fillOpacity: 0.65,
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

        layer.on({
          mouseover: (e) => {
            const poly = e.target;
            poly.setStyle({
              weight: 2.5,
              color: '#ffffff',
              fillOpacity: 0.85,
            });
            poly.bringToFront();
          },
          mouseout: (e) => {
            geoJsonLayer.resetStyle(e.target);
          },
          click: () => {
            onSelectConstituency(props.ac_no);
          },
        });
      },
    }).addTo(map);

    map.fitBounds(geoJsonLayer.getBounds(), { padding: [10, 10] });

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [viewMode, spatialData, onSelectConstituency]);

  return (
    <div className="statewide-map-workspace animate-fade-in">
      <div className="map-workspace-header">
        <div>
          <h2>Statewide Strategic Cluster Map</h2>
          <p className="map-intro-text">
            Bihar campaign terrain mapped by assembly boundaries. Toggle 3D projection view to analyze electoral density.
          </p>
        </div>
        <div className="view-mode-tabs">
          <button 
            className={`tab-btn ${viewMode === '2d' ? 'active' : ''}`}
            onClick={() => setViewMode('2d')}
          >
            2D Flat Map
          </button>
          <button 
            className={`tab-btn ${viewMode === '3d' ? 'active' : ''}`}
            onClick={() => setViewMode('3d')}
          >
            3D Hologram Projection
          </button>
        </div>
      </div>

      <div className="map-grid-layout">
        {/* Map View Panel */}
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
          
          {viewMode === '2d' ? (
            <div ref={containerRef} className="leaflet-map-element" />
          ) : (
            spatialData && (
              <div className="canvas-3d-wrapper">
                <div className="metric-select-container">
                  <span className="select-lbl">Project Metric Height:</span>
                  <div className="metric-btn-group">
                    <button 
                      className={`metric-btn ${metric3D === 'turnout' ? 'active' : ''}`}
                      onClick={() => setMetric3D('turnout')}
                    >
                      Turnout %
                    </button>
                    <button 
                      className={`metric-btn ${metric3D === 'competitiveness' ? 'active' : ''}`}
                      onClick={() => setMetric3D('competitiveness')}
                    >
                      Competitiveness
                    </button>
                    <button 
                      className={`metric-btn ${metric3D === 'welfare' ? 'active' : ''}`}
                      onClick={() => setMetric3D('welfare')}
                    >
                      Welfare Score
                    </button>
                  </div>
                </div>
                <Map3DCanvas 
                  features={spatialData.features} 
                  metric={metric3D}
                  onSelectConstituency={onSelectConstituency}
                />
              </div>
            )
          )}
        </div>

        {/* Legend Panel */}
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
        .map-workspace-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1.5rem;
          gap: 1.5rem;
        }
        @media (max-width: 768px) {
          .map-workspace-header {
            flex-direction: column;
          }
        }
        .map-intro-text {
          font-size: 0.9rem;
          color: var(--text-secondary);
          margin-top: 0.25rem;
        }
        .view-mode-tabs {
          display: flex;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          padding: 3px;
        }
        .tab-btn {
          background: transparent;
          border: none;
          color: #94a3b8;
          padding: 0.5rem 1rem;
          font-size: 0.85rem;
          font-weight: 600;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }
        .tab-btn:hover {
          color: #fff;
        }
        .tab-btn.active {
          background: rgba(99, 102, 241, 0.15);
          color: #c7d2fe;
          border: 1px solid rgba(99, 102, 241, 0.2);
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
        .canvas-3d-wrapper {
          position: relative;
          width: 100%;
          height: 100%;
          background: #08090d;
          border-radius: calc(var(--radius-lg) - 0.5rem);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          overflow: hidden;
        }
        .canvas-container-3d {
          position: relative;
          width: 100%;
          height: 100%;
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .metric-select-container {
          position: absolute;
          top: 1rem;
          left: 1rem;
          z-index: 5;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          background: rgba(8, 9, 13, 0.85);
          backdrop-filter: blur(8px);
          padding: 0.5rem 0.75rem;
          border-radius: 8px;
          border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .select-lbl {
          font-size: 0.75rem;
          color: #94a3b8;
          font-weight: 600;
        }
        .metric-btn-group {
          display: flex;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 6px;
          padding: 2px;
        }
        .metric-btn {
          background: transparent;
          border: none;
          color: #64748b;
          padding: 0.35rem 0.75rem;
          font-size: 0.75rem;
          font-weight: 600;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.15s;
        }
        .metric-btn:hover {
          color: #fff;
        }
        .metric-btn.active {
          background: rgba(168, 85, 247, 0.15);
          color: #f3e8ff;
          border: 1px solid rgba(168, 85, 247, 0.2);
        }
        .dossier-hover-panel {
          position: absolute;
          bottom: 1.5rem;
          right: 1.5rem;
          width: 250px;
          padding: 1rem;
          z-index: 5;
          pointer-events: none;
          background: rgba(10, 11, 16, 0.95);
          border: 1px solid rgba(255, 255, 255, 0.08);
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
        }
        .hover-ac-no {
          font-size: 0.65rem;
          font-weight: 700;
          color: #a855f7;
          letter-spacing: 0.05em;
          text-transform: uppercase;
        }
        .hover-ac-name {
          font-size: 1.15rem;
          font-weight: 700;
          color: #fff;
          margin-bottom: 0.05rem;
        }
        .hover-ac-district {
          font-size: 0.75rem;
          color: #94a3b8;
        }
        .hover-ac-persona {
          font-size: 0.75rem;
          font-weight: 700;
          margin-top: 0.25rem;
        }
        .hover-divider {
          height: 1px;
          background: rgba(255, 255, 255, 0.08);
          margin: 0.5rem 0;
        }
        .hover-stat {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
          margin-bottom: 0.2rem;
        }
        .stat-lbl {
          color: #64748b;
        }
        .stat-val {
          color: #f1f5f9;
        }
        .hover-click-tip {
          font-size: 0.65rem;
          color: #a855f7;
          text-align: center;
          margin-top: 0.6rem;
          font-style: italic;
          font-weight: 500;
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
