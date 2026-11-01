export function UsageMeter({
  label,
  used,
  limit,
}: {
  label: string;
  used: number;
  limit: number | null;
}) {
  const pct = limit ? Math.min(100, Math.round((used / limit) * 100)) : 0;
  return (
    <div className="border border-line rounded-md bg-panel p-4">
      <div className="flex items-baseline justify-between mb-2">
        <span className="text-sm text-muted">{label}</span>
        <span className="font-mono text-sm text-paper">
          {used}
          {limit !== null ? ` / ${limit}` : " / Unlimited"}
        </span>
      </div>
      {limit !== null && (
        <div className="h-1.5 rounded-full bg-ink overflow-hidden">
          <div
            className="h-full bg-signal transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
    </div>
  );
}
