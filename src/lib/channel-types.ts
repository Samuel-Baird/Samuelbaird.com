/**
 * Visual styling for channel type pills.
 *
 * Each known type maps to a Tailwind background + text color pair. Unknown
 * types fall back to a muted gray so new types added later still render
 * cleanly without code changes.
 *
 * Tailwind v4 needs the full color class names to appear in source (no
 * dynamic string concatenation), so we keep them as literal strings here.
 */

export type TypeColor = { bg: string; text: string };

const NEUTRAL: TypeColor = {
  bg: "bg-[color:var(--muted-soft)]",
  text: "text-[color:var(--muted)]",
};

export const TYPE_COLORS: Record<string, TypeColor> = {
  // Faith-promoting / scholarship
  Apologetics: { bg: "bg-emerald-100", text: "text-emerald-800" },
  Religious: { bg: "bg-blue-100", text: "text-blue-800" },
  Church: { bg: "bg-indigo-100", text: "text-indigo-800" },
  Education: { bg: "bg-teal-100", text: "text-teal-800" },
  "Church History": { bg: "bg-stone-200", text: "text-stone-700" },
  BYU: { bg: "bg-sky-100", text: "text-sky-800" },
  "Gen. Conf. Video Reposts": { bg: "bg-violet-100", text: "text-violet-800" },
  "General Religious": { bg: "bg-blue-100", text: "text-blue-800" },
  Ancestry: { bg: "bg-amber-100", text: "text-amber-800" },

  // Critical / outside
  Critical: { bg: "bg-rose-100", text: "text-rose-800" },
  Investigator: { bg: "bg-orange-100", text: "text-orange-800" },
  Politics: { bg: "bg-orange-100", text: "text-orange-800" },
  "Not LDS": { bg: "bg-stone-200", text: "text-stone-700" },

  // Lifestyle / culture
  Music: { bg: "bg-pink-100", text: "text-pink-800" },
  Children: { bg: "bg-lime-100", text: "text-lime-800" },
  Youth: { bg: "bg-lime-100", text: "text-lime-800" },

  // Media
  News: { bg: "bg-slate-200", text: "text-slate-700" },
  TV: { bg: "bg-slate-200", text: "text-slate-700" },
  Business: { bg: "bg-zinc-200", text: "text-zinc-700" },
};

export function colorsForType(type: string | null | undefined): TypeColor {
  if (!type) return NEUTRAL;
  return TYPE_COLORS[type] ?? NEUTRAL;
}
