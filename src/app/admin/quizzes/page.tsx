import { requireAdmin } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { fmtNumber } from "@/lib/format";
import {
  BIRTH_DECADE_OPTIONS,
  COUNTRY_OPTIONS,
  EDUCATION_OPTIONS,
  GENDER_OPTIONS,
  HISPANIC_OPTIONS,
  MARITAL_OPTIONS,
  RACE_OPTIONS,
  RELIGION_GROUPS,
  RELIGION_OPTIONS,
  STATE_OPTIONS,
  religionOption,
  type ReligionGroup,
} from "@/lib/evangelical-quiz/demographics";
import { QUIZ_DATA } from "@/lib/evangelical-quiz";

export const dynamic = "force-dynamic";

/**
 * Per-quiz results for the site owner. Structured as one section per quiz
 * so future quizzes (e.g. the timeline quiz) slot in as siblings; only the
 * evangelical quiz's section is built today. Reads evangelical_quiz_runs
 * (deny-all RLS) through the service client, aggregates in JS like
 * /admin/analytics.
 *
 * The demographic breakdowns follow Pew's RLS variables (migration 0047),
 * so a column here lines up with a column in Pew's published tables.
 */

type RunRow = {
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
  score: number;
  percentile: number;
  matched_tradition: string | null;
  tie: boolean;
  created_at: string;
};

const MATCHABLE = ["Evangelical", "Black Protestant", "Mainline", "Roman Catholic"];

/** Legacy only - the intake stopped asking for age at migration 0047. */
const AGE_BUCKETS: { label: string; min: number; max: number }[] = [
  { label: "Under 18", min: 1, max: 17 },
  { label: "18–29", min: 18, max: 29 },
  { label: "30–44", min: 30, max: 44 },
  { label: "45–64", min: 45, max: 64 },
  { label: "65+", min: 65, max: 110 },
];

/**
 * The quiz tradition a whole religion group corresponds to. Every option in
 * a group shares one (that's what makes it a group), so the first answers
 * for all of them.
 */
const GROUP_TRADITION = new Map<ReligionGroup, string | null>(
  RELIGION_GROUPS.map((group) => [
    group,
    RELIGION_OPTIONS.find((o) => o.group === group)?.quizTradition ?? null,
  ]),
);

function daysAgoIso(days: number) {
  return new Date(Date.now() - days * 86_400_000).toISOString();
}

function countBy<T>(rows: T[], key: (row: T) => string): Map<string, number> {
  const map = new Map<string, number>();
  for (const row of rows) {
    const k = key(row);
    map.set(k, (map.get(k) ?? 0) + 1);
  }
  return map;
}

/**
 * Counts one demographic field in its option list's own order, so a
 * breakdown reads like the question did - never sorted by size, which would
 * shuffle ordinal answers like birth decade or education.
 */
function tally(
  runs: RunRow[],
  options: readonly { slug: string; label: string }[],
  value: (run: RunRow) => string | null,
): { label: string; count: number; muted?: boolean }[] {
  const counts = countBy(runs, (r) => value(r) ?? "__none__");
  const rows = options
    .map((o) => ({ label: o.label, count: counts.get(o.slug) ?? 0 }))
    .filter((r) => r.count > 0);
  return [...rows, { label: "Not provided", count: counts.get("__none__") ?? 0, muted: true }];
}

export default async function AdminQuizzesPage() {
  await requireAdmin();

  const sb = createSupabaseServiceClient();
  const { data } = await sb
    .from("evangelical_quiz_runs")
    .select(
      "user_id, age, birth_decade, gender, hispanic, race, education, marital_status, country, us_state, tradition_slug, score, percentile, matched_tradition, tie, created_at",
    )
    .order("created_at", { ascending: false });
  const runs = (data ?? []) as RunRow[];

  return (
    <div className="space-y-12">
      <header>
        <h1 className="serif text-3xl font-semibold tracking-tight">Quizzes</h1>
        <p className="mt-2 max-w-2xl text-sm text-[color:var(--muted)]">
          Completed runs, one row per completion (retakes count again). Scores are
          recomputed server-side at recording time; demographics are the optional
          intake snapshot, asked in Pew&apos;s Religious Landscape Study wording.
        </p>
      </header>

      <EvangelicalQuizSection runs={runs} />
    </div>
  );
}

function EvangelicalQuizSection({ runs }: { runs: RunRow[] }) {
  const since30 = daysAgoIso(30);
  const total = runs.length;
  const signedIn = runs.filter((r) => r.user_id !== null).length;
  const last30 = runs.filter((r) => r.created_at >= since30).length;

  // Percentile deciles.
  const deciles = new Array<number>(10).fill(0);
  for (const r of runs) {
    const d = Math.min(9, Math.floor(r.percentile / 10));
    deciles[d] += 1;
  }
  const decileMax = Math.max(1, ...deciles);

  // Matched-tradition counts.
  const matchedCounts = countBy(runs, (r) =>
    r.tie ? "Tie" : (r.matched_tradition ?? "No match"),
  );

  // Self-reported x matched crosstab, at the group level: with 53 religions
  // in the picker a row-per-religion table would be mostly zeroes, and the
  // agreement diagonal is a group-level claim anyway (any evangelical
  // Protestant family should match "Evangelical").
  const crosstabRows = [
    ...RELIGION_GROUPS.map((group) => ({
      key: group as string,
      label: group as string,
      quizTradition: GROUP_TRADITION.get(group) ?? null,
    })),
    { key: "__none__", label: "Not provided", quizTradition: null },
  ];
  const cell = new Map<string, number>();
  for (const r of runs) {
    const self = religionOption(r.tradition_slug)?.group ?? "__none__";
    const matched = r.tie ? "Tie" : (r.matched_tradition ?? "—");
    const k = `${self}|${matched}`;
    cell.set(k, (cell.get(k) ?? 0) + 1);
  }
  const crosstabCols = [...MATCHABLE, "Tie"];

  // Self-reported religion in full detail, grouped as the picker groups it.
  const religionCounts = countBy(runs, (r) => r.tradition_slug ?? "__none__");
  const religionGroups = RELIGION_GROUPS.map((group) => ({
    group,
    options: RELIGION_OPTIONS.filter(
      (o) => o.group === group && (religionCounts.get(o.slug) ?? 0) > 0,
    ).map((o) => ({ label: o.label, count: religionCounts.get(o.slug) ?? 0 })),
  })).filter((g) => g.options.length > 0);
  const religionMissing = religionCounts.get("__none__") ?? 0;

  // Legacy age, from runs recorded before birth cohort replaced it.
  const legacyAge = runs.filter((r) => r.age !== null);

  return (
    <section className="space-y-8">
      <div className="flex flex-wrap items-baseline justify-between gap-3 border-b border-[color:var(--border)] pb-3">
        <h2 className="serif text-2xl font-semibold tracking-tight">
          How evangelical are you?
        </h2>
        <a
          href="/api/exports/admin-evangelical-quiz-runs.csv"
          className="text-xs font-medium text-[color:var(--accent)] hover:underline"
          download
        >
          Download runs CSV
        </a>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Tile label="Completed runs" value={fmtNumber(total)} />
        <Tile
          label="Signed-in / anonymous"
          value={`${fmtNumber(signedIn)} / ${fmtNumber(total - signedIn)}`}
        />
        <Tile label="Last 30 days" value={fmtNumber(last30)} />
      </div>

      {total === 0 ? (
        <p className="text-sm text-[color:var(--muted)]">
          No completed runs recorded yet.
        </p>
      ) : (
        <>
          <div>
            <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Evangelical percentile distribution
            </h3>
            <ul className="mt-3 space-y-1.5">
              {deciles.map((count, i) => (
                <li key={i} className="flex items-center gap-3 text-xs">
                  <span className="w-16 shrink-0 tabular-nums text-[color:var(--muted)]">
                    {i * 10}–{i * 10 + 10}
                  </span>
                  <span className="h-3.5 flex-1 overflow-hidden rounded-[var(--radius)] bg-[color:var(--muted-soft)]">
                    <span
                      className="block h-full bg-[color:var(--accent)]"
                      style={{ width: `${(count / decileMax) * 100}%` }}
                    />
                  </span>
                  <span className="w-10 shrink-0 text-right tabular-nums">{fmtNumber(count)}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Matched tradition
            </h3>
            <ul className="mt-3 space-y-1.5 text-sm">
              {[...matchedCounts.entries()]
                .sort((a, b) => b[1] - a[1])
                .map(([label, count]) => (
                  <li key={label} className="flex justify-between gap-4">
                    <span>{label}</span>
                    <span className="tabular-nums">{fmtNumber(count)}</span>
                  </li>
                ))}
            </ul>
          </div>

          <div>
            <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Self-reported religion × matched tradition
            </h3>
            <p className="mt-1 text-xs text-[color:var(--muted)]">
              Rows are Pew&apos;s RELTRAD groups. Highlighted cells are agreement — the
              self-reported group maps to the matched tradition.
            </p>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full min-w-[540px] border-collapse text-xs">
                <thead>
                  <tr className="border-b border-[color:var(--border)] text-left">
                    <th className="py-1.5 pr-3 font-medium">Self-reported</th>
                    {crosstabCols.map((c) => (
                      <th key={c} className="px-2 py-1.5 text-right font-medium">
                        {c}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {crosstabRows.map((row) => (
                    <tr key={row.key} className="border-b border-[color:var(--border)]/60">
                      <td className="py-1.5 pr-3">{row.label}</td>
                      {crosstabCols.map((c) => {
                        const count = cell.get(`${row.key}|${c}`) ?? 0;
                        const agree = row.quizTradition !== null && row.quizTradition === c;
                        return (
                          <td
                            key={c}
                            className={`px-2 py-1.5 text-right tabular-nums ${
                              agree ? "bg-[color:var(--honey-soft)] font-semibold" : ""
                            } ${count === 0 ? "text-[color:var(--muted)]" : ""}`}
                          >
                            {count}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Self-reported religion
            </h3>
            <p className="mt-1 text-xs text-[color:var(--muted)]">
              Pew&apos;s FAMILY taxonomy. Categories nobody chose are left out.
            </p>
            <div className="mt-3 grid gap-6 sm:grid-cols-2">
              {religionGroups.map(({ group, options }) => (
                <div key={group}>
                  <h4 className="text-xs font-semibold">{group}</h4>
                  <ul className="mt-1.5 space-y-1.5 text-sm">
                    {options.map((o) => (
                      <li key={o.label} className="flex justify-between gap-4">
                        <span>{o.label}</span>
                        <span className="tabular-nums">{fmtNumber(o.count)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
            <p className="mt-3 text-xs text-[color:var(--muted)]">
              Not provided: {fmtNumber(religionMissing)}
            </p>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            <Breakdown
              title="Birth cohort"
              rows={tally(runs, BIRTH_DECADE_OPTIONS, (r) => r.birth_decade)}
            />
            <Breakdown
              title="Gender"
              rows={tally(runs, GENDER_OPTIONS, (r) => r.gender)}
            />
            <Breakdown
              title="Hispanic origin"
              rows={tally(runs, HISPANIC_OPTIONS, (r) => r.hispanic)}
            />
            <Breakdown title="Race" rows={tally(runs, RACE_OPTIONS, (r) => r.race)} />
            <Breakdown
              title="Education"
              rows={tally(runs, EDUCATION_OPTIONS, (r) => r.education)}
            />
            <Breakdown
              title="Marital status"
              rows={tally(runs, MARITAL_OPTIONS, (r) => r.marital_status)}
            />
          </div>

          <Breakdown
            title="Country"
            rows={tally(runs, COUNTRY_OPTIONS, (r) => r.country)}
            columns
          />

          <Breakdown
            title="State"
            rows={tally(runs, STATE_OPTIONS, (r) => r.us_state)}
            columns
          />

          {legacyAge.length > 0 && (
            <div>
              <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                Age (legacy)
              </h3>
              <p className="mt-1 text-xs text-[color:var(--muted)]">
                From {fmtNumber(legacyAge.length)} runs recorded before the intake
                switched to Pew&apos;s birth-cohort question.
              </p>
              <ul className="mt-3 space-y-1.5 text-sm">
                {AGE_BUCKETS.map((b) => (
                  <li key={b.label} className="flex justify-between gap-4">
                    <span>{b.label}</span>
                    <span className="tabular-nums">
                      {fmtNumber(
                        legacyAge.filter((r) => r.age! >= b.min && r.age! <= b.max).length,
                      )}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <p className="text-xs text-[color:var(--muted)]">
            Data version {QUIZ_DATA.data_version} · {QUIZ_DATA.items.length} statements ·
            demographics mirror Pew Research Center&apos;s 2023-24 Religious Landscape
            Study (doi: 10.58094/3kwb-bf52). Runs before data v3 recorded a percentile
            against a simulated population; the decile chart above mixes both
            definitions for runs of different vintages.
          </p>
        </>
      )}
    </section>
  );
}

function Breakdown({
  title,
  rows,
  columns = false,
}: {
  title: string;
  rows: { label: string; count: number; muted?: boolean }[];
  /** For long lists (states) - wrap into columns rather than one tall list. */
  columns?: boolean;
}) {
  return (
    <div>
      <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">{title}</h3>
      <ul
        className={`mt-3 space-y-1.5 text-sm ${columns ? "sm:columns-2 lg:columns-3" : ""}`}
      >
        {rows.map((r) => (
          <li
            key={r.label}
            className={`flex justify-between gap-4 ${
              r.muted ? "text-[color:var(--muted)]" : ""
            }`}
          >
            <span>{r.label}</span>
            <span className="tabular-nums">{fmtNumber(r.count)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5">
      <p className="small-caps text-[11px] text-[color:var(--muted)]">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums">{value}</p>
    </div>
  );
}
