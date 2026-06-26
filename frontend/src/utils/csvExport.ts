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

const escapeCSV = (val: any): string => {
  if (val === null || val === undefined) return '';
  let str = String(val);
  str = str.replace(/"/g, '""');
  if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
    return `"${str}"`;
  }
  return str;
};

export const exportComparisonToCsv = (dossiers: DossierData[]): void => {
  if (dossiers.length === 0) return;

  // Build the CSV header row: "Metric", "Constituency 1 Name (AC #1)", ...
  const headers = [
    'Metric',
    ...dossiers.map((d) => `${d.name} (AC #${d.id})`)
  ];

  // Define each metric row name and how to pull it from a dossier object
  const rowsConfig: { label: string; getValue: (d: DossierData) => any }[] = [
    // General
    { label: 'AC Number', getValue: (d) => d.id },
    { label: 'District', getValue: (d) => d.district },
    { label: 'State', getValue: (d) => d.state },
    { label: 'Electoral Status', getValue: (d) => {
        const p2025 = d.electoral_history.election_2025?.winner_party;
        const p2020 = d.electoral_history.election_2020?.winner_party;
        if (!p2025 || !p2020) return 'N/A';
        return p2025 === p2020 ? `${p2025} HOLD` : `${p2025} FLIP from ${p2020}`;
      }
    },
    // 2025 Result
    { label: '2025 Winner Candidate', getValue: (d) => d.electoral_history.election_2025?.winner_name },
    { label: '2025 Winner Party', getValue: (d) => d.electoral_history.election_2025?.winner_party },
    { label: '2025 Victory Margin', getValue: (d) => d.electoral_history.election_2025?.margin },
    { label: '2025 Turnout (%)', getValue: (d) => d.electoral_history.election_2025?.voter_turnout_pct },
    // 2020 Result
    { label: '2020 Winner Candidate', getValue: (d) => d.electoral_history.election_2020?.winner_name },
    { label: '2020 Winner Party', getValue: (d) => d.electoral_history.election_2020?.winner_party },
    { label: '2020 Victory Margin', getValue: (d) => d.electoral_history.election_2020?.margin },
    { label: '2020 Turnout (%)', getValue: (d) => d.electoral_history.election_2020?.voter_turnout_pct },
    // Demographics
    { label: 'Total Population', getValue: (d) => d.demographics?.total_population },
    { label: 'Literacy Rate (%)', getValue: (d) => d.demographics?.literacy_rate_pct },
    { label: 'Urban Population (%)', getValue: (d) => d.demographics?.urban_ratio_pct },
    { label: 'Rural Population (%)', getValue: (d) => d.demographics?.rural_ratio_pct },
    { label: 'Scheduled Caste SC (%)', getValue: (d) => d.demographics?.sc_ratio_pct },
    { label: 'Scheduled Tribe ST (%)', getValue: (d) => d.demographics?.st_ratio_pct },
    { label: 'Hindu Population (%)', getValue: (d) => d.demographics?.hindu_ratio_pct },
    { label: 'Muslim Population (%)', getValue: (d) => d.demographics?.muslim_ratio_pct },
    // Schemes
    { label: 'Welfare Composite Score', getValue: (d) => d.scheme_exposure?.scheme_penetration_score },
    { label: 'Active MGNREGA Job Cards', getValue: (d) => d.scheme_exposure?.mgnrega_active_job_cards },
    { label: 'PMAY Homes Sanctioned', getValue: (d) => d.scheme_exposure?.pmay_homes_sanctioned },
    { label: 'PMAY Homes Completed', getValue: (d) => d.scheme_exposure?.pmay_homes_completed },
    { label: 'Ujjwala Gas Connections', getValue: (d) => d.scheme_exposure?.ujjwala_gas_connections },
    { label: 'MGNREGA Penetration (%)', getValue: (d) => d.scheme_exposure?.mgnrega_penetration_pct },
    { label: 'PMAY Completion Rate (%)', getValue: (d) => d.scheme_exposure?.pmay_completion_rate },
    { label: 'PMAY Penetration (%)', getValue: (d) => d.scheme_exposure?.pmay_penetration_pct },
    { label: 'Ujjwala Penetration (%)', getValue: (d) => d.scheme_exposure?.ujjwala_penetration_pct },
    { label: 'Welfare Data is District Estimate', getValue: (d) => d.scheme_exposure?.scheme_data_is_district_estimate ? 'True' : 'False' },
    // Discourse
    { label: 'Discourse: Development (%)', getValue: (d) => d.discourse_topics?.topics.development },
    { label: 'Discourse: Jobs & Unemployment (%)', getValue: (d) => d.discourse_topics?.topics.unemployment },
    { label: 'Discourse: Welfare & Schemes (%)', getValue: (d) => d.discourse_topics?.topics.welfare },
    { label: 'Discourse: Caste Dynamics (%)', getValue: (d) => d.discourse_topics?.topics.caste },
    { label: 'Discourse: Communal (%)', getValue: (d) => d.discourse_topics?.topics.communal },
    { label: 'Discourse Coverage is Sparse', getValue: (d) => d.discourse_topics?.discourse_data_sparse ? 'True' : 'False' },
    // Strategy
    { label: 'Assigned Strategic Segment', getValue: (d) => d.cluster_assignment?.persona_name },
    { label: 'Rule-Based Strategy recommendation', getValue: (d) => d.messaging_recommendation?.recommendation_text },
    { label: 'AI Suggested Phrasing / Slogan', getValue: (d) => d.messaging_recommendation?.example_phrasing }
  ];

  // Assemble CSV rows
  const csvLines: string[] = [];
  
  // 1. Headers line
  csvLines.push(headers.map(escapeCSV).join(','));

  // 2. Data lines
  rowsConfig.forEach((row) => {
    const lineCells = [
      row.label,
      ...dossiers.map((d) => row.getValue(d))
    ];
    csvLines.push(lineCells.map(escapeCSV).join(','));
  });

  const csvString = csvLines.join('\n');

  // Trigger browser download
  const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', 'constituency_comparison_report.csv');
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
