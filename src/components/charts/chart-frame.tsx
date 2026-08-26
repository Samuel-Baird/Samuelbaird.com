/**
 * The house chart anatomy: eyebrow, title, subtitle, plot area, caption.
 * Server-safe (no "use client") — the frame is pure markup; the plot inside
 * `children` brings its own interactivity where it needs it.
 *
 * Title is set in Fraunces (the house headline font) rather than a bold
 * sans, at roughly the same ~2.5x-over-body ratio Burge's Product Sans
 * titles use. See docs/CHARTS.md "Anatomy" for the full reasoning.
 */
export function ChartFrame({
  eyebrow,
  title,
  subtitle,
  caption,
  children,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  caption?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
      <div>
        {eyebrow ? (
          <div className="small-caps text-[11px] font-medium text-[color:var(--honey)]">
            {eyebrow}
          </div>
        ) : null}
        <h3 className="serif mt-1 text-lg font-semibold tracking-tight sm:text-xl">
          {title}
        </h3>
        {subtitle ? (
          <p className="mt-1 text-sm text-[color:var(--muted)]">{subtitle}</p>
        ) : null}
      </div>
      <div className="mt-4">{children}</div>
      {caption ? (
        <div className="mt-4 text-[11px] text-[color:var(--muted)]">{caption}</div>
      ) : null}
    </div>
  );
}

/** `Data: <source> · latterdaystats.com`, the fixed caption grammar. Pass
 * `via` for a curator credit ("CCES via Ryan Burge"). */
export function ChartCaption({
  source,
  via,
  note,
}: {
  source: string;
  via?: string;
  note?: string;
}) {
  return (
    <>
      Data: {source}
      {via ? ` via ${via}` : ""} · latterdaystats.com
      {note ? <> — {note}</> : null}
    </>
  );
}
