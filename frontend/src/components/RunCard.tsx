import type { RunRecord, VariantRecord } from "../types";

const shortHash = (hash: string) => hash ? `${hash.slice(0, 12)}…` : "Unavailable";

export function RunCard({ run, expected }: { run: RunRecord; expected: VariantRecord }) {
  const recovery = run.exact_recovery === true ? "Recovered" : run.exact_recovery === false ? "Not recovered" : "Unavailable";
  return (
    <article className="run-card">
      <div className="run-card__heading">
        <div><p className="micro-label">Pipeline profile</p><h3>{run.profile}</h3></div>
        <span className={`run-status run-status--${run.status}`}>{run.status}</span>
      </div>
      <div className="recovery-line">
        <span className={`recovery-symbol recovery-symbol--${run.exact_recovery === true ? "yes" : run.exact_recovery === false ? "no" : "na"}`} aria-hidden="true">
          {run.exact_recovery === true ? "✓" : run.exact_recovery === false ? "×" : "—"}
        </span>
        <div><span>Exact marker</span><strong>{recovery}</strong></div>
      </div>
      <dl className="detail-list">
        <div><dt>Execution</dt><dd>Daytona sandbox</dd></div>
        <div><dt>Sandbox ID</dt><dd title={run.sandbox_id || undefined}>{run.sandbox_id || "Unavailable"}</dd></div>
        <div><dt>Caller</dt><dd>{run.caller} {run.caller_version}</dd></div>
        <div><dt>Fixture hash</dt><dd className="mono" title={run.fixture_sha256}>{shortHash(run.fixture_sha256)}</dd></div>
        <div><dt>Config hash</dt><dd className="mono" title={run.config_sha256}>{shortHash(run.config_sha256)}</dd></div>
        <div><dt>Expected</dt><dd>pos {expected.position} · {expected.length_bp} bp</dd></div>
        <div><dt>Detected</dt><dd>{run.detected_position == null ? "No exact call" : `pos ${run.detected_position} · ${run.detected_length_bp ?? "—"} bp`}</dd></div>
      </dl>
      {run.error && <p className="run-error">{run.error}</p>}
    </article>
  );
}
