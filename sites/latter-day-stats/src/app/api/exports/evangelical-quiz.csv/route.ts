import { NextResponse } from "next/server";
import { toCsv } from "@/lib/csv";
import { fiveColumnPct, QUIZ_DATA } from "@/lib/evangelical-quiz";

const GROUP_ORDER = [
  "Evangelical",
  "Black Protestant",
  "Mainline",
  "Roman Catholic",
  "All U.S. adults",
];

type Row = { itemId: string; statement: string; year: number | null; group: string; pcts: number[] };

export async function GET() {
  const rows: Row[] = [];
  for (const item of QUIZ_DATA.items) {
    for (const group of GROUP_ORDER) {
      const pcts = fiveColumnPct(item, group);
      if (!pcts) continue;
      rows.push({ itemId: item.id, statement: item.statement, year: item.year, group, pcts });
    }
  }

  // Same layout as the source workbook (scripts/evangelical-quiz/build_data.py
  // reads), minus the total_check formula column.
  const csv = toCsv(rows, [
    { header: "item_id", value: (r) => r.itemId },
    { header: "statement", value: (r) => r.statement },
    { header: "year", value: (r) => r.year ?? "" },
    { header: "group", value: (r) => r.group },
    { header: "strongly_disagree", value: (r) => r.pcts[0] },
    { header: "somewhat_disagree", value: (r) => r.pcts[1] },
    { header: "not_sure", value: (r) => r.pcts[2] },
    { header: "somewhat_agree", value: (r) => r.pcts[3] },
    { header: "strongly_agree", value: (r) => r.pcts[4] },
  ]);

  return new NextResponse(`﻿${csv}`, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": 'attachment; filename="latter-day-stats-evangelical-quiz-data.csv"',
      "Cache-Control": "private, no-store",
    },
  });
}
