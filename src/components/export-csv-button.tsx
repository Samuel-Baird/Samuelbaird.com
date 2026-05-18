"use client";

import { Download } from "lucide-react";
import { downloadCsv, toCsv, type CsvColumn } from "@/lib/csv";

type Props<T> = {
  rows: T[];
  columns: CsvColumn<T>[];
  filename: string;
  label?: string;
};

export function ExportCsvButton<T>({
  rows,
  columns,
  filename,
  label = "Export CSV",
}: Props<T>) {
  function onClick() {
    const csv = toCsv(rows, columns);
    downloadCsv(filename, csv);
  }
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={rows.length === 0}
      className="inline-flex h-11 items-center gap-2 rounded-full border border-[color:var(--border)] bg-white px-4 text-sm font-medium hover:bg-[color:var(--muted-soft)] disabled:opacity-60"
      title={`${label} (${rows.length} rows)`}
    >
      <Download aria-hidden="true" size={16} />
      {label}
      <span className="text-xs text-[color:var(--muted)]">({rows.length})</span>
    </button>
  );
}
