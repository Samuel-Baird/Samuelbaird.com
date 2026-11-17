import type { CSSProperties, ReactNode } from "react";

export const OG_SIZE = { width: 1200, height: 630 };
export const OG_CONTENT_TYPE = "image/png";

// Archive palette, hardcoded — satori can't read globals.css or CSS vars.
// Keep these in sync with src/app/globals.css :root values.
export const OG_PAPER = "#f4eeda";
export const OG_INK = "#1a1a1a";
export const OG_MUTED = "#6b6b6b";
export const OG_BORDER = "#e6e3dd";
export const OG_ACCENT = "#1f4f7a";
export const OG_HONEY = "#8a5a06";

const FRAME: CSSProperties = {
  width: "100%",
  height: "100%",
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  background: OG_PAPER,
  padding: "64px 72px",
  fontFamily: "Georgia, serif",
  borderTop: `6px solid ${OG_HONEY}`,
  borderBottom: `1px solid ${OG_BORDER}`,
};

const EYEBROW: CSSProperties = {
  fontSize: 18,
  color: OG_HONEY,
  fontFamily: "system-ui, sans-serif",
  letterSpacing: "0.14em",
  textTransform: "uppercase",
  fontWeight: 600,
};

const FOOTER: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
  fontSize: 18,
  color: OG_MUTED,
  fontFamily: "system-ui, sans-serif",
};

// Raw SVG markup for the beehive mark, inlined for satori — see
// src/components/beehive-mark.tsx for the canonical React component this
// mirrors. Satori has limited support for arbitrary imported components, so
// OG frames render the paths directly instead of <BeehiveMark />.
function BeehiveGlyph({ size = 20, color = OG_HONEY }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <g stroke={color} strokeWidth="1.15" strokeLinecap="round">
        <path d="M12 2.6c1.7 1.15 2.7 2.2 2.7 3.35 0 .95-.9 1.4-2.7 1.4s-2.7-.45-2.7-1.4c0-1.15 1-2.2 2.7-3.35Z" />
        <path d="M8.15 8.3c1.05.55 2.35.85 3.85.85s2.8-.3 3.85-.85c.75.85 1.15 1.7 1.15 2.55 0 1.15-1.6 1.75-5 1.75s-5-.6-5-1.75c0-.85.4-1.7 1.15-2.55Z" />
        <path d="M6.35 13.55c1.4.65 3.35 1 5.65 1s4.25-.35 5.65-1c.9 1 1.35 1.95 1.35 2.9 0 1.35-2.55 2.05-7 2.05s-7-.7-7-2.05c0-.95.45-1.9 1.35-2.9Z" />
        <path d="M4.6 19.35c1.85.75 4.45 1.15 7.4 1.15s5.55-.4 7.4-1.15" />
      </g>
      <circle cx="12" cy="11.7" r=".55" fill={color} stroke="none" />
    </svg>
  );
}

export function OgFrame({
  eyebrow,
  children,
}: {
  eyebrow: string;
  children: ReactNode;
}) {
  return (
    <div style={FRAME}>
      <span style={EYEBROW}>{eyebrow}</span>
      {children}
      <div style={FOOTER}>
        <BeehiveGlyph />
        <span>samuelbaird.com/latter-day-stats</span>
      </div>
    </div>
  );
}
