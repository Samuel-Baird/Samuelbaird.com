import type { CSSProperties, ReactNode } from "react";

export const OG_SIZE = { width: 1200, height: 630 };
export const OG_CONTENT_TYPE = "image/png";

const FRAME: CSSProperties = {
  width: "100%",
  height: "100%",
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  background: "#ffffff",
  padding: "64px 72px",
  fontFamily: "Georgia, serif",
};

const EYEBROW: CSSProperties = {
  fontSize: 18,
  color: "#6b7280",
  fontFamily: "system-ui, sans-serif",
  letterSpacing: "0.1em",
  textTransform: "uppercase",
};

const FOOTER: CSSProperties = {
  fontSize: 18,
  color: "#9ca3af",
  fontFamily: "system-ui, sans-serif",
};

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
      <div style={FOOTER}>latter-day-stats.vercel.app</div>
    </div>
  );
}
