export type ProfileName = "compatible" | "changed" | "corrected";
export type Verdict =
  | "COMPUTATIONALLY_OBSERVABLE"
  | "NOT_TECHNICALLY_COMPARABLE"
  | "NO_CONCLUSION";

export interface HealthResponse {
  status: string;
  service: string;
  integrations: {
    daytona_configured: boolean;
    neo4j_configured: boolean;
  };
  clinical_use: false;
}

export interface VariantRecord {
  gene: "FLT3";
  type: "ITD";
  position: number;
  length_bp: number;
  sequence: string;
  test_vaf: number;
}

export interface RunRecord {
  run_id: string;
  profile: ProfileName;
  status: "completed" | "failed";
  sandbox_id: string | null;
  caller: string;
  caller_version: string;
  config_sha256: string;
  fixture_sha256: string;
  exact_recovery: boolean | null;
  detected_position: number | null;
  detected_length_bp: number | null;
  detected_sequence: string | null;
  error: string | null;
}

export interface HandoffResponse {
  case_id: string;
  fixture_id: string;
  synthetic: boolean;
  variant: VariantRecord;
  runs: RunRecord[];
  verdict: Verdict;
  verdict_source: "neo4j";
  limitations: string[];
}

export type ResultSource = "live" | "demo" | "error";
