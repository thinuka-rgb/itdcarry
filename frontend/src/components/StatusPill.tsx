interface StatusPillProps {
  label: string;
  state: "ready" | "offline" | "neutral" | "demo";
}

export function StatusPill({ label, state }: StatusPillProps) {
  return (
    <span className={`status-pill status-pill--${state}`}>
      <span className="status-pill__dot" aria-hidden="true" />
      {label}
    </span>
  );
}
