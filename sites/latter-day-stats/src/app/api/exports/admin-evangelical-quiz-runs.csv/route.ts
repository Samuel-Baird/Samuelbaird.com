import { NextResponse } from "next/server";
import { requireAdmin } from "@/lib/auth";
import { toCsv } from "@/lib/csv";
import { QUIZ_DATA } from "@/lib/evangelical-quiz";
import { religionOption, rlsCodes } from "@/lib/evangelical-quiz/demographics";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

type RunRow = {
  id: string;
  user_id: string | null;
  age: number | null;
  birth_decade: string | null;
  gender: string | null;
  hispanic: string | null;
  race: string | null;
  education: string | null;
  marital_status: string | null;
  country: string | null;
  us_state: string | null;
  /** Migration 0046's name for the religion slug. */
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

/** A run row's answers as RLS codes. See rlsCodes() for what null means. */
function rls(r: RunRow) {
  return rlsCodes({
    age: r.age,
    birthDecade: r.birth_decade,
    gender: r.gender,
    hispanic: r.hispanic,
    race: r.race,
    education: r.education,
    maritalStatus: r.marital_status,
    country: r.country,
    state: r.us_state,
    religionSlug: r.tradition_slug,
  });
}

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
      "id, user_id, age, birth_decade, gender, hispanic, race, education, marital_status, country, us_state, tradition_slug, answers, score, percentile, matched_tradition, runner_up_tradition, tie, data_version, created_at",
    )
    .order("created_at", { ascending: true });
  if (error) throw error;
  const runs = (data ?? []) as RunRow[];

  const csv = toCsv(runs, [
    { header: "run_id", value: (r) => r.id },
    { header: "created_at", value: (r) => r.created_at },
    { header: "respondent_type", value: (r) => (r.user_id ? "user" : "anonymous") },
    // Demographics twice over: the site's own slug, then the RLS code for
    // the same answer, so the export drops straight into an analysis run
    // against Pew's national file without a recode pass.
    { header: "religion_slug", value: (r) => r.tradition_slug ?? "" },
    { header: "religion_group", value: (r) => religionOption(r.tradition_slug)?.group ?? "" },
    { header: "rls_family", value: (r) => rls(r).FAMILY ?? "" },
    { header: "birth_decade", value: (r) => r.birth_decade ?? "" },
    { header: "rls_birthdecade", value: (r) => rls(r).BIRTHDECADE ?? "" },
    { header: "gender", value: (r) => r.gender ?? "" },
    { header: "rls_gender", value: (r) => rls(r).GENDER ?? "" },
    { header: "hispanic", value: (r) => r.hispanic ?? "" },
    { header: "rls_hisp", value: (r) => rls(r).HISP ?? "" },
    { header: "race", value: (r) => r.race ?? "" },
    { header: "rls_racecmb", value: (r) => rls(r).RACECMB ?? "" },
    { header: "education", value: (r) => r.education ?? "" },
    { header: "rls_educrec", value: (r) => rls(r).EDUCREC ?? "" },
    { header: "marital_status", value: (r) => r.marital_status ?? "" },
    { header: "rls_marital", value: (r) => rls(r).MARITAL ?? "" },
    { header: "country", value: (r) => r.country ?? "" },
    { header: "state", value: (r) => r.us_state ?? "" },
    // Retired question, kept so runs recorded before the RLS switch export
    // everything they hold.
    { header: "age_legacy", value: (r) => r.age ?? "" },
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
