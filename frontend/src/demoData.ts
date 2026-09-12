import type { HandoffResponse } from "./types";

export const demoResponse: HandoffResponse = {
  case_id: "AML-DEMO-001",
  fixture_id: "FLT3-ITD-DEMO-001",
  synthetic: true,
  variant: {
    gene: "FLT3",
    type: "ITD",
    position: 72,
    length_bp: 21,
    sequence: "TCTCTGAATATGATCTCAAAT",
    test_vaf: 0.1,
  },
  runs: [
    {
      run_id: "demo-compatible",
      profile: "compatible",
      status: "completed",
      sandbox_id: "demo-sandbox-not-live",
      caller: "getITD",
      caller_version: "1.5.17",
      config_sha256: "8a6a0dd60a3a87f02863b0f715fbf6f09eb254d4101892a51f5908b44c9c3861",
      fixture_sha256: "7b1ea5912135ba56a9b4fd1c852fdbfd619629d5c79b3c23744a121225c9d119",
      exact_recovery: true,
      detected_position: 72,
      detected_length_bp: 21,
      detected_sequence: "TCTCTGAATATGATCTCAAAT",
      error: null,
    },
  ],
  verdict: "COMPUTATIONALLY_OBSERVABLE",
  verdict_source: "neo4j",
  limitations: [
    "Illustrative demo data only; this screen is not evidence of a live execution.",
    "Computational recovery does not validate the physical assay or establish disease status.",
    "ITDCarry is not intended for diagnosis, treatment, remission, relapse, or MRD decisions.",
  ],
};
