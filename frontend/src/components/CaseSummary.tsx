export function CaseSummary() {
  return (
    <aside className="case-card" aria-label="Fictional case summary">
      <div className="case-card__topline">
        <span>Case AML-DEMO-001</span>
        <span className="tag">Fictional case</span>
      </div>
      <div className="case-card__marker">
        <div className="gene-mark" aria-hidden="true">F3</div>
        <div>
          <p className="micro-label">Known diagnostic marker</p>
          <h2>FLT3 internal tandem duplication</h2>
        </div>
      </div>
      <div className="case-card__followup">
        <span className="followup-icon" aria-hidden="true">↓</span>
        <div>
          <p className="micro-label">Later report</p>
          <strong>FLT3-ITD “not detected”</strong>
          <p>Pipeline configuration changed</p>
        </div>
      </div>
    </aside>
  );
}
