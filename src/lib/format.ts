export function fmtCompact(n: number | null | undefined): string {
  if (n == null) return "—";
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(n);
}

export function fmtNumber(n: number | null | undefined): string {
  if (n == null) return "—";
  return new Intl.NumberFormat("en-US").format(n);
}

export function fmtYearsSince(iso: string | null | undefined): string {
  if (!iso) return "—";
  const start = new Date(iso).getTime();
  if (isNaN(start)) return "—";
  const years = (Date.now() - start) / (365.25 * 24 * 3600 * 1000);
  if (years < 1) return `${Math.round(years * 12)} mo`;
  return `${years.toFixed(1)} yr`;
}

export function fmtAvgViews(
  views: number | null | undefined,
  videos: number | null | undefined,
): string {
  if (!views || !videos) return "—";
  return fmtCompact(Math.round(views / videos));
}

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
