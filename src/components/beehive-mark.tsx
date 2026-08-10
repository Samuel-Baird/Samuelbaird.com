/**
 * A line-drawn skep (beehive), the site's identity mark. Deseret seasoning
 * on the Archive direction: used sparingly as the nav wordmark's glyph, the
 * favicon/app icon, an OG-image mark, and the dinkus between sections.
 *
 * Drawn as stroked arcs rather than a filled icon so it reads as an
 * engraving, not a clip-art bee logo. currentColor lets callers set honey,
 * ink, or muted depending on context.
 */
export function BeehiveMark({
  className,
  title,
}: {
  className?: string;
  title?: string;
}) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      role={title ? "img" : "presentation"}
      aria-hidden={title ? undefined : true}
    >
      {title ? <title>{title}</title> : null}
      <g stroke="currentColor" strokeWidth="1.15" strokeLinecap="round">
        <path d="M12 2.6c1.7 1.15 2.7 2.2 2.7 3.35 0 .95-.9 1.4-2.7 1.4s-2.7-.45-2.7-1.4c0-1.15 1-2.2 2.7-3.35Z" />
        <path d="M8.15 8.3c1.05.55 2.35.85 3.85.85s2.8-.3 3.85-.85c.75.85 1.15 1.7 1.15 2.55 0 1.15-1.6 1.75-5 1.75s-5-.6-5-1.75c0-.85.4-1.7 1.15-2.55Z" />
        <path d="M6.35 13.55c1.4.65 3.35 1 5.65 1s4.25-.35 5.65-1c.9 1 1.35 1.95 1.35 2.9 0 1.35-2.55 2.05-7 2.05s-7-.7-7-2.05c0-.95.45-1.9 1.35-2.9Z" />
        <path d="M4.6 19.35c1.85.75 4.45 1.15 7.4 1.15s5.55-.4 7.4-1.15" />
      </g>
      <circle cx="12" cy="11.7" r=".55" fill="currentColor" stroke="none" />
    </svg>
  );
}
