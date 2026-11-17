import {
  BEEHIVE_BANDS,
  BEEHIVE_BARS,
  BEEHIVE_BAR_BASELINE,
  BEEHIVE_BAR_WIDTH,
} from "@/lib/beehive-stats-mark";

/**
 * The filled beehive-and-bar-chart mark used as the favicon (see
 * src/app/icon.tsx, which shares this geometry). Two-tone by design —
 * honey bands, ink bars — unlike the single-color line-drawn
 * <BeehiveMark>, which stays the engraving-style identity mark elsewhere
 * (footer wordmark, section dinkus).
 */
export function BeehiveStatsMark({
  className,
  title,
}: {
  className?: string;
  title?: string;
}) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className}
      role={title ? "img" : "presentation"}
      aria-hidden={title ? undefined : true}
    >
      {title ? <title>{title}</title> : null}
      {BEEHIVE_BANDS.map((b, i) => (
        <rect
          key={i}
          x={b.x}
          y={b.y}
          width={b.w}
          height={b.h}
          rx={b.rx}
          fill="var(--honey)"
        />
      ))}
      {BEEHIVE_BARS.map((b, i) => (
        <rect
          key={i}
          x={b.x}
          y={BEEHIVE_BAR_BASELINE - b.h}
          width={BEEHIVE_BAR_WIDTH}
          height={b.h}
          rx={0.6}
          fill="var(--foreground)"
        />
      ))}
    </svg>
  );
}
