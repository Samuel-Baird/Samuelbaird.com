import { NextResponse } from "next/server";
import { requireAdmin } from "@/lib/auth";
import { toCsv } from "@/lib/csv";
import { QUIZ_DATA } from "@/lib/evangelical-quiz";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

type RunRow = {
  id: string;
  user_id: string | null;
  age: number | null;
  gender: string | null;
  tradition_slug: string | null;
  answers: Record<string, number> | null;
  score: number;
  percentile: number;
  matched_tradition: string | null;
  runner_up_tradition: string | null;
  tie: boolean;
  data_version: string;
  created_at: string;
};

/**
 * Admin-only export of completed evangelical-quiz runs, one row per run,
 * with a column per statement (response label, not index). Deliberately
 * pseudonymous even for the admin: respondent_type says user/anonymous but
 * the raw user_id/anon_id never leave the database - the disclosure
 * promises aggregate research, and the export honors that.
 */
export async function GET() {
  await requireAdmin();

  const sb = createSupabaseServiceClient();
  const { data, error } = await sb
    .from("evangelical_quiz_runs")
    .select(
      "id, user_id, age, gender, tradition_slug, answers, score, percentile, matched_tradition, runner_up_tradition, tie, data_version, created_at",
    )
    .order("created_at", { ascending: true });
  if (error) throw error;
  const runs = (data ?? []) as RunRow[];

  const csv = toCsv(runs, [
    { header: "run_id", value: (r) => r.id },
    { header: "created_at", value: (r) => r.created_at },
    { header: "respondent_type", value: (r) => (r.user_id ? "user" : "anonymous") },
    { header: "age", value: (r) => r.age ?? "" },
    { header: "gender", value: (r) => r.gender ?? "" },
    { header: "tradition_slug", value: (r) => r.tradition_slug ?? "" },
    { header: "score", value: (r) => r.score },
    { header: "percentile", value: (r) => r.percentile },
    { header: "matched_tradition", value: (r) => r.matched_tradition ?? "" },
    { header: "runner_up_tradition", value: (r) => r.runner_up_tradition ?? "" },
    { header: "tie", value: (r) => (r.tie ? "true" : "false") },
    { header: "data_version", value: (r) => r.data_version },
    ...QUIZ_DATA.items.map((item) => ({
      header: item.id,
      value: (r: RunRow) => {
        const idx = r.answers?.[item.id];
        return typeof idx === "number" ? (item.scale[idx] ?? "") : "";
      },
    })),
  ]);

  return new NextResponse(`﻿${csv}`, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition":
        'attachment; filename="latter-day-stats-evangelical-quiz-runs.csv"',
      "Cache-Control": "private, no-store",
    },
  });
}
