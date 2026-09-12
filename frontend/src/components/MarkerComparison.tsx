import type { RunRecord, VariantRecord } from "../types";

export function MarkerComparison({ expected, runs }: { expected: VariantRecord; runs: RunRecord[] }) {
  return (
    <section className="comparison panel" aria-labelledby="comparison-title">
      <div className="section-heading compact">
        <div><p className="eyebrow">Marker evidence</p><h2 id="comparison-title">Expected and detected</h2></div>
        <span className="tag">Deterministic comparison</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Source</th><th>Position</th><th>Length</th><th>Sequence</th></tr></thead>
          <tbody>
            <tr><th>Expected marker</th><td>{expected.position}</td><td>{expected.length_bp} bp</td><td className="sequence">{expected.sequence}</td></tr>
            {runs.map((run) => (
              <tr key={run.run_id}>
                <th>{run.profile}</th>
                <td>{run.detected_position ?? "—"}</td>
                <td>{run.detected_length_bp == null ? "—" : `${run.detected_length_bp} bp`}</td>
                <td className="sequence">{run.detected_sequence || "No detected sequence"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="table-note">Exact recovery is supplied by the backend; the browser does not interpret sequence equivalence.</p>
    </section>
  );
}
