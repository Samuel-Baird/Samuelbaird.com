/**
 * Shared label treatment for the Archive direction: square corners,
 * small caps, a hairline ring, tinted text over a faint tint background.
 * Replaces the old fully-rounded, Tailwind-pastel pill used across
 * channel-type badges, timeline category tags, and status/verify badges.
 */

export type TagInk = "ink" | "accent" | "oxblood" | "honey" | "muted";

const INK: Record<TagInk, { text: string; ring: string; bg: string }> = {
  ink: {
    text: "text-[color:var(--foreground)]",
    ring: "ring-[color:var(--foreground)]/25",
    bg: "bg-[color:var(--foreground)]/[0.04]",
  },
  accent: {
    text: "text-[color:var(--accent)]",
    ring: "ring-[color:var(--accent)]/35",
    bg: "bg-[color:var(--accent-soft)]",
  },
  oxblood: {
    text: "text-[color:var(--oxblood)]",
    ring: "ring-[color:var(--oxblood)]/35",
    bg: "bg-[color:var(--oxblood-soft)]",
  },
  honey: {
    text: "text-[color:var(--honey)]",
    ring: "ring-[color:var(--honey)]/35",
    bg: "bg-[color:var(--honey-soft)]",
  },
  muted: {
    text: "text-[color:var(--muted)]",
    ring: "ring-[color:var(--border)]",
    bg: "bg-[color:var(--muted-soft)]",
  },
};

export function Tag({
  children,
  ink = "muted",
  title,
  className = "",
}: {
  children: React.ReactNode;
  ink?: TagInk;
  title?: string;
  className?: string;
}) {
  const c = INK[ink];
  return (
    <span
      title={title}
      className={`small-caps inline-flex items-center rounded-[var(--radius)] ${c.bg} ${c.text} ring-1 ${c.ring} px-2 py-0.5 text-[11px] font-medium ${title ? "cursor-help" : ""} ${className}`}
    >
      {children}
    </span>
  );
}
