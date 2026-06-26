import { useState, useEffect } from 'react';
import './App.css';
import { SearchAutocomplete } from './components/SearchAutocomplete';
import { DossierHeader } from './components/DossierHeader';
import { ElectoralHistory } from './components/ElectoralHistory';
import { DemographicSection } from './components/DemographicSection';
import { WelfareExposure } from './components/WelfareExposure';
import { DiscourseTopics } from './components/DiscourseTopics';
import { StrategicPersona } from './components/StrategicPersona';
import { RecommendationPanel } from './components/RecommendationPanel';

// Comparison View Imports
import { ConstituencyMultiSelect } from './components/ConstituencyMultiSelect';
import { ComparisonTable } from './components/ComparisonTable';
import { exportComparisonToCsv } from './utils/csvExport';

// Statewide Map Import
import { StatewideMap } from './components/StatewideMap';

const API_BASE = 'http://localhost:8000';

interface ConstituencyItem {
  id: number;
  name: string;
  district: string;
  cluster_id: number | null;
}

interface MemberConstituency {
  id: number;
  name: string;
  district: string;
}

interface DossierData {
  id: number;
  name: string;
  district: string;
  state: string;
  electoral_history: {
    election_2025: any;
    election_2020: any;
  };
  demographics: any;
  scheme_exposure: any;
  nfhs_indicators: any;
  discourse_topics: any;
  cluster_assignment: any;
  messaging_recommendation: any;
  metadata: any;
}

function App() {
  const [constituencies, setConstituencies] = useState<ConstituencyItem[]>([]);
  const [activeTab, setActiveTab] = useState<'dossier' | 'compare' | 'map'>('dossier');

  // Dossier View States
  const [activeId, setActiveId] = useState<number | null>(1); // Default to Valmiki Nagar (AC #1)
  const [dossier, setDossier] = useState<DossierData | null>(null);
  const [clusterMembers, setClusterMembers] = useState<MemberConstituency[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingMembers, setLoadingMembers] = useState<boolean>(false);
  const [exportLoading, setExportLoading] = useState<boolean>(false);
  const [dossierError, setDossierError] = useState<string | null>(null);

  // Comparison View States
  const [selectedCompareIds, setSelectedCompareIds] = useState<number[]>([1, 2]); // Default compared ACs
  const [compareData, setCompareData] = useState<DossierData[]>([]);
  const [compareLoading, setCompareLoading] = useState<boolean>(false);
  const [compareError, setCompareError] = useState<string | null>(null);

  // 1. Fetch constituencies list on mount
  useEffect(() => {
    const fetchList = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/constituencies`);
        if (!res.ok) throw new Error('Failed to fetch constituencies list');
        const data = await res.json();
        setConstituencies(data);
      } catch (err: any) {
        console.error(err);
        setDossierError('Unable to load constituencies. Make sure backend is running on http://localhost:8000');
      }
    };
    fetchList();
  }, []);

  // 2. Fetch single constituency dossier
  useEffect(() => {
    if (activeId === null || activeTab !== 'dossier') return;

    const fetchDossier = async () => {
      setLoading(true);
      setDossierError(null);
      try {
        const res = await fetch(`${API_BASE}/api/constituency/${activeId}`);
        if (!res.ok) throw new Error(`Failed to fetch dossier for AC #${activeId}`);
        const data = await res.json();
        setDossier(data);
        
        // Fetch cluster members if available
        if (data.cluster_assignment && data.cluster_assignment.cluster_id !== undefined) {
          fetchClusterMembers(data.cluster_assignment.cluster_id);
        } else {
          setClusterMembers([]);
        }
      } catch (err: any) {
        console.error(err);
        setDossierError(err.message || 'Error fetching constituency data');
      } finally {
        setLoading(false);
      }
    };

    fetchDossier();
  }, [activeId, activeTab]);

  // 3. Fetch comparison data when selectedCompareIds changes
  useEffect(() => {
    if (activeTab !== 'compare') return;
    if (selectedCompareIds.length < 2) {
      setCompareData([]);
      return;
    }

    const fetchComparison = async () => {
      setCompareLoading(true);
      setCompareError(null);
      try {
        const idsQuery = selectedCompareIds.join(',');
        const res = await fetch(`${API_BASE}/api/compare?ids=${idsQuery}`);
        if (!res.ok) throw new Error('Failed to load comparison dossiers');
        const data = await res.json();
        setCompareData(data);
      } catch (err: any) {
        console.error(err);
        setCompareError(err.message || 'Error fetching comparison data');
      } finally {
        setCompareLoading(false);
      }
    };

    fetchComparison();
  }, [selectedCompareIds, activeTab]);

  // Fetch similar peer constituencies from cluster endpoint
  const fetchClusterMembers = async (clusterId: number) => {
    setLoadingMembers(true);
    try {
      const res = await fetch(`${API_BASE}/api/cluster/${clusterId}`);
      if (res.ok) {
        const data = await res.json();
        setClusterMembers(data.members || []);
      }
    } catch (err) {
      console.error('Error fetching cluster members:', err);
    } finally {
      setLoadingMembers(false);
    }
  };

  // Handle PDF Export
  const handleExportPdf = async () => {
    if (activeId === null) return;
    setExportLoading(true);
    try {
      window.open(`${API_BASE}/api/constituency/${activeId}/export`, '_blank');
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setTimeout(() => setExportLoading(false), 1500);
    }
  };

  // Multi-select actions
  const handleAddCompareId = (id: number) => {
    if (selectedCompareIds.length >= 5) return;
    setSelectedCompareIds((prev) => [...prev, id]);
  };

  const handleRemoveCompareId = (id: number) => {
    setSelectedCompareIds((prev) => prev.filter((item) => item !== id));
  };

  const handleExportComparisonCsv = () => {
    exportComparisonToCsv(compareData);
  };

  return (
    <div className="app-container">
      {/* Navbar / Top Bar */}
      <header className="app-navbar glass-panel animate-fade-in">
        <div className="logo-section">
          <span className="logo-badge">IQ</span>
          <div>
            <h1>ConstituencyIQ</h1>
            <p className="subtitle">Bihar AC 2025 Campaign Intelligence Console</p>
          </div>
        </div>

        {/* Tab Selection Navigation */}
        <nav className="tab-navigation">
          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'dossier' ? 'active' : ''}`}
            onClick={() => setActiveTab('dossier')}
          >
            📋 Constituency Dossier
          </button>
          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'compare' ? 'active' : ''}`}
            onClick={() => setActiveTab('compare')}
          >
            📊 Compare Matrix
          </button>
          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'map' ? 'active' : ''}`}
            onClick={() => setActiveTab('map')}
          >
            🗺️ Statewide Map
          </button>
        </nav>

        <div className="status-indicator">
          <span className="pulse-dot"></span> Server Active
        </div>
      </header>

      {/* VIEW 1: SINGLE DOSSIER VIEW */}
      {activeTab === 'dossier' && (
        <>
          {/* Global Error Banner */}
          {dossierError && (
            <div className="error-banner animate-fade-in">
              <span className="error-icon">⚠️</span>
              <div className="error-text">{dossierError}</div>
              <button type="button" className="retry-btn" onClick={() => setActiveId(activeId || 1)}>Retry</button>
            </div>
          )}

          {/* Search / Autocomplete Box */}
          <div className="dashboard-controls">
            <SearchAutocomplete
              constituencies={constituencies}
              onSelect={(id) => setActiveId(id)}
              activeId={activeId}
            />
          </div>

          {/* Loading Overlay */}
          {loading && (
            <div className="dashboard-loading-state">
              <div className="spinner-wrapper">
                <span className="spinner large"></span>
                <p>Assembling intelligence dossier...</p>
              </div>
            </div>
          )}

          {/* Main Dossier Contents */}
          {!loading && dossier && (
            <main className="dashboard-layout animate-fade-in">
              {/* Header row spans full width */}
              <div className="layout-row span-full">
                <DossierHeader
                  id={dossier.id}
                  name={dossier.name}
                  district={dossier.district}
                  state={dossier.state}
                  election2025={dossier.electoral_history.election_2025}
                  election2020={dossier.electoral_history.election_2020}
                  metadata={dossier.metadata}
                  onExport={handleExportPdf}
                  exportLoading={exportLoading}
                />
              </div>

              {/* Left Column: Demographics & History */}
              <div className="layout-col left-col">
                <ElectoralHistory
                  election2025={dossier.electoral_history.election_2025}
                  election2020={dossier.electoral_history.election_2020}
                  metadata={dossier.metadata}
                />
                <DemographicSection
                  demographics={dossier.demographics}
                  nfhs={dossier.nfhs_indicators}
                  metadata={dossier.metadata}
                />
              </div>

              {/* Right Column: Welfare, Discourse, Persona & recommendations */}
              <div className="layout-col right-col">
                <WelfareExposure
                  schemeData={dossier.scheme_exposure}
                  metadata={dossier.metadata}
                />
                <DiscourseTopics
                  discourseData={dossier.discourse_topics}
                  metadata={dossier.metadata}
                />
                <StrategicPersona
                  assignment={dossier.cluster_assignment}
                  members={clusterMembers}
                  activeId={dossier.id}
                  onSelectMember={(id) => setActiveId(id)}
                  loadingMembers={loadingMembers}
                />
                <RecommendationPanel
                  recommendation={dossier.messaging_recommendation}
                />
              </div>
            </main>
          )}
        </>
      )}

      {/* VIEW 2: COMPARISON VIEW */}
      {activeTab === 'compare' && (
        <>
          {/* Comparison Error Banner */}
          {compareError && (
            <div className="error-banner animate-fade-in">
              <span className="error-icon">⚠️</span>
              <div className="error-text">{compareError}</div>
              <button type="button" className="retry-btn" onClick={() => setSelectedCompareIds([...selectedCompareIds])}>Retry</button>
            </div>
          )}

          {/* Constituency Multi-Select Component */}
          <div className="dashboard-controls">
            <ConstituencyMultiSelect
              constituencies={constituencies}
              selectedIds={selectedCompareIds}
              onAdd={handleAddCompareId}
              onRemove={handleRemoveCompareId}
            />
          </div>

          {/* Loading state */}
          {compareLoading && (
            <div className="dashboard-loading-state">
              <div className="spinner-wrapper">
                <span className="spinner large"></span>
                <p>Generating comparative analytics grid...</p>
              </div>
            </div>
          )}

          {/* Side-by-Side Comparison Matrix */}
          {!compareLoading && selectedCompareIds.length >= 2 && compareData.length > 0 && (
            <main className="comparison-layout span-full animate-fade-in">
              <ComparisonTable
                dossiers={compareData}
                onExportCsv={handleExportComparisonCsv}
              />
            </main>
          )}
        </>
      )}

      {/* VIEW 3: STATEWIDE MAP VIEW */}
      {activeTab === 'map' && (
        <main className="span-full animate-fade-in">
          <StatewideMap
            onSelectConstituency={(id) => {
              setActiveId(id);
              setActiveTab('dossier');
            }}
          />
        </main>
      )}

      <footer className="dashboard-footer">
        <p>© 2026 BoothIQ Campaign Analytics. Confidential Briefing — Internal Strategy Use Only.</p>
      </footer>
    </div>
  );
}

export default App;
