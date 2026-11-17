"use client";

import { useMemo, useState } from "react";

export type TableColumn = { key: string; label: string };
export type TableRow = { name: string; cells: Record<string, number | null> };

const nf = new Intl.NumberFormat("en-US");

/** Sortable table: click a header to sort, click again to reverse. Rows with no
 * value stay at the bottom either way. */
export function DataTable({
  rows,
  columns,
  nameLabel,
  highlight,
}: {
  rows: TableRow[];
  columns: TableColumn[];
  nameLabel: string;
  highlight?: string;
}) {
  const [sort, setSort] = useState<{ key: string; dir: "asc" | "desc" }>({ key: "members", dir: "desc" });

  const sorted = useMemo(() => {
    const sign = sort.dir === "asc" ? 1 : -1;
    return [...rows].sort((x, y) => {
      if (sort.key === "name") return x.name.localeCompare(y.name) * sign;
      const a = x.cells[sort.key] ?? null;
      const b = y.cells[sort.key] ?? null;
      if (a === null && b === null) return 0;
      if (a === null) return 1;
      if (b === null) return -1;
      return (a - b) * sign;
    });
  }, [rows, sort]);

  function sortBy(key: string) {
    setSort((s) =>
      s.key === key
        ? { key, dir: s.dir === "asc" ? "desc" : "asc" }
        : { key, dir: key === "name" ? "asc" : "desc" },
    );
  }

  const all = [{ key: "name", label: nameLabel }, ...columns];

  return (
    <div className="max-h-[36rem] overflow-auto">
      <table className="w-full min-w-[640px] text-sm tabular-nums">
        <thead className="sticky top-0 bg-[color:var(--background)]">
          <tr className="border-b border-[color:var(--border)] text-left text-[color:var(--muted)]">
            {all.map((c, i) => (
              <th
                key={c.key}
                scope="col"
                aria-sort={sort.key === c.key ? (sort.dir === "asc" ? "ascending" : "descending") : "none"}
                className={`py-2 pr-3 font-medium ${i === 0 ? "" : "text-right"}`}
              >
                <button
                  type="button"
                  onClick={() => sortBy(c.key)}
                  className={`inline-flex items-center gap-1 hover:text-[color:var(--foreground)] ${sort.key === c.key ? "text-[color:var(--foreground)]" : ""}`}
                >
                  {c.label}
                  <span aria-hidden="true" className="w-3 text-[10px]">
                    {sort.key === c.key ? (sort.dir === "asc" ? "▲" : "▼") : ""}
                  </span>
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((r) => (
            <tr key={r.name} className="border-b border-[color:var(--border)] last:border-0">
              <td className="py-2 pr-3">{r.name}</td>
              {columns.map((c) => {
                const v = r.cells[c.key];
                return (
                  <td
                    key={c.key}
                    className={`py-2 pr-3 text-right ${c.key === highlight ? "font-medium text-[color:var(--foreground)]" : ""}`}
                  >
                    {v === null || v === undefined ? "—" : nf.format(v)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
