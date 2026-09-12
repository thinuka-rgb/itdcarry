import type { ResultSource, Verdict } from "../types";

const content: Record<Verdict, { icon: string; title: string; copy: string; tone: string }> = {
  COMPUTATIONALLY_OBSERVABLE: {
    icon: "✓",
    title: "Computationally observable",
    copy: "The tested pipeline recovered the exact synthetic marker under the disclosed computational conditions.",
    tone: "pass",
  },
  NOT_TECHNICALLY_COMPARABLE: {
    icon: "!",
    title: "Not technically comparable",
    copy: "The pipeline completed but did not recover the exact synthetic marker. No biological conclusion is made.",
    tone: "miss",
  },
  NO_CONCLUSION: {
    icon: "—",
    title: "No conclusion",
    copy: "The challenge could not be completed or verified, so no observability conclusion can be made.",
    tone: "unknown",
  },
};

export function VerdictPanel({ verdict, source }: { verdict: Verdict; source: ResultSource }) {
  const item = content[verdict];
  return (
    <section className={`verdict verdict--${item.tone}`} aria-live="polite">
      <div className="verdict__icon" aria-hidden="true">{item.icon}</div>
      <div className="verdict__body">
        <div className="verdict__label-row">
          <p className="eyebrow">Computational verdict</p>
          <span className={`source-badge source-badge--${source}`}>
            {source === "live" ? "Live API result" : source === "demo" ? "Illustrative demo data" : "Verification unavailable"}
          </span>
        </div>
        <h2>{item.title}</h2>
        <p>{item.copy}</p>
        {source !== "error" && <span className="neo-source">◆ Verdict source: Neo4j</span>}
      </div>
    </section>
  );
}
