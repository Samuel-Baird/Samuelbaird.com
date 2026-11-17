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

export function fmtRelative(
  iso: string | null | undefined,
): { text: string; fresh: boolean } {
  if (!iso) return { text: "Unknown", fresh: false };
  const t = new Date(iso).getTime();
  if (isNaN(t)) return { text: "Unknown", fresh: false };
  const diff = Date.now() - t;
  const m = Math.floor(diff / 60_000);
  const h = Math.floor(diff / 3_600_000);
  const d = Math.floor(diff / 86_400_000);
  const fresh = d < 7;
  let text: string;
  if (m < 60) text = `${Math.max(1, m)}m ago`;
  else if (h < 24) text = `${h}h ago`;
  else if (d < 30) text = `${d}d ago`;
  else text = fmtDate(iso);
  return { text, fresh };
}

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "America/Denver",
  });
}

export function fmtDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "—";
  return d.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZone: "America/Denver",
    timeZoneName: "short",
  });
}
