import { Download } from "lucide-react";

type Props = {
  href: string;
  rowCount: number;
  label?: string;
};

export function ExportCsvButton({ href, rowCount, label = "Export CSV" }: Props) {
  return (
    <a
      href={href}
      className={`inline-flex h-11 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm font-medium text-[color:var(--foreground)] hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)] ${
        rowCount === 0 ? "pointer-events-none opacity-60" : ""
      }`}
      title={`${label} (${rowCount} rows)`}
      aria-disabled={rowCount === 0}
    >
      <Download aria-hidden="true" size={16} />
      {label}
      <span className="text-xs text-[color:var(--muted)]">({rowCount})</span>
    </a>
  );
}
