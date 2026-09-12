import type { ProfileName } from "../types";

interface ChallengeFlowProps {
  running: boolean;
  corrected: boolean;
  onCorrectedChange: (selected: boolean) => void;
  onRun: () => void;
}

const stages = [
  ["01", "Known marker", "Exact diagnostic ITD"],
  ["02", "Synthetic challenge", "Controlled paired-end reads"],
  ["03", "Follow-up pipeline", "Pinned computational profile"],
] as const;

export function ChallengeFlow({ running, corrected, onCorrectedChange, onRun }: ChallengeFlowProps) {
  const profiles: ProfileName[] = corrected ? ["compatible", "changed", "corrected"] : ["compatible", "changed"];
  return (
    <section className="challenge-panel" aria-labelledby="challenge-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Controlled challenge</p>
          <h2 id="challenge-title">Test technical observability</h2>
        </div>
        <label className="profile-toggle">
          <input
            type="checkbox"
            checked={corrected}
            onChange={(event) => onCorrectedChange(event.target.checked)}
            disabled={running}
          />
          Include corrected profile
        </label>
      </div>
      <div className="flow" aria-label="Challenge workflow">
        {stages.map(([number, title, copy], index) => (
          <div className="flow-item-wrap" key={title}>
            <div className="flow-item">
              <span className="flow-number">{number}</span>
              <div><strong>{title}</strong><span>{copy}</span></div>
            </div>
            {index < stages.length - 1 && <span className="flow-arrow" aria-hidden="true">→</span>}
          </div>
        ))}
      </div>
      {running && (
        <div className="progress-box" role="status" aria-live="polite">
          <span className="spinner" aria-hidden="true" />
          <div>
            <strong>Awaiting verified result</strong>
            <p>Daytona execution → exact comparison → Neo4j verdict</p>
          </div>
        </div>
      )}
      <div className="challenge-actions">
        <button className="primary-button" type="button" onClick={onRun} disabled={running}>
          {running ? "Challenge in progress…" : "Run observability challenge"}
          {!running && <span aria-hidden="true">→</span>}
        </button>
        <p>{profiles.join(" + ")} · Same synthetic fixture</p>
      </div>
    </section>
  );
}
