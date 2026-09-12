export function Limitations({ items }: { items: string[] }) {
  return (
    <section className="limitations" aria-labelledby="limitations-title">
      <div className="limitations__icon" aria-hidden="true">i</div>
      <div>
        <h2 id="limitations-title">Synthetic computational proof of concept — not for clinical use</h2>
        <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
      </div>
    </section>
  );
}
