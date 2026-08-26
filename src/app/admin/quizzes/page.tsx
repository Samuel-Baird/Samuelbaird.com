import { requireAdmin } from "@/lib/auth";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { fmtNumber } from "@/lib/format";
import { TRADITION_OPTIONS } from "@/lib/evangelical-quiz/demographics";
import { QUIZ_DATA } from "@/lib/evangelical-quiz";

export const dynamic = "force-dynamic";

/**
 * Per-quiz results for the site owner. Structured as one section per quiz
 * so future quizzes (e.g. the timeline quiz) slot in as siblings; only the
 * evangelical quiz's section is built today. Reads evangelical_quiz_runs
 * (deny-all RLS) through the service client, aggregates in JS like
 * /admin/analytics.
 */

type RunRow = {
  user_id: string | null;
  age: number | null;
  gender: string | null;
  tradition_slug: string | null;
  score: number;
  percentile: number;
  matched_tradition: string | null;
  tie: boolean;
  created_at: string;
};

const MATCHABLE = ["Evangelical", "Black Protestant", "Mainline", "Roman Catholic"];

const AGE_BUCKETS: { label: string; min: number; max: number }[] = [
  { label: "Under 18", min: 1, max: 17 },
  { label: "18–29", min: 18, max: 29 },
  { label: "30–44", min: 30, max: 44 },
  { label: "45–64", min: 45, max: 64 },
  { label: "65+", min: 65, max: 110 },
];

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

export default async function AdminQuizzesPage() {
  await requireAdmin();

  const sb = createSupabaseServiceClient();
  const { data } = await sb
    .from("evangelical_quiz_runs")
    .select(
      "user_id, age, gender, tradition_slug, score, percentile, matched_tradition, tie, created_at",
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
          intake snapshot.
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

  // Self-reported x matched crosstab.
  const crosstabRows = [
    ...TRADITION_OPTIONS,
    { slug: "__none__", label: "Not provided", pewCategory: null },
  ];
  const cell = new Map<string, number>();
  for (const r of runs) {
    const self = r.tradition_slug ?? "__none__";
    const matched = r.tie ? "Tie" : (r.matched_tradition ?? "—");
    const k = `${self}|${matched}`;
    cell.set(k, (cell.get(k) ?? 0) + 1);
  }
  const crosstabCols = [...MATCHABLE, "Tie"];

  // Demographics.
  const ageCounts = AGE_BUCKETS.map((b) => ({
    label: b.label,
    count: runs.filter((r) => r.age !== null && r.age >= b.min && r.age <= b.max).length,
  }));
  const ageMissing = runs.filter((r) => r.age === null).length;
  const genderCounts = countBy(runs, (r) => r.gender ?? "Not provided");
  const traditionLabel = new Map(TRADITION_OPTIONS.map((t) => [t.slug, t.label]));

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
              Self-reported tradition × matched tradition
            </h3>
            <p className="mt-1 text-xs text-[color:var(--muted)]">
              Highlighted cells are agreement — the self-reported tradition maps to the
              matched one.
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
                    <tr key={row.slug} className="border-b border-[color:var(--border)]/60">
                      <td className="py-1.5 pr-3">{row.label}</td>
                      {crosstabCols.map((c) => {
                        const count = cell.get(`${row.slug}|${c}`) ?? 0;
                        const agree = row.pewCategory !== null && row.pewCategory === c;
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

          <div className="grid gap-8 sm:grid-cols-2">
            <div>
              <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                Age
              </h3>
              <ul className="mt-3 space-y-1.5 text-sm">
                {ageCounts.map((b) => (
                  <li key={b.label} className="flex justify-between gap-4">
                    <span>{b.label}</span>
                    <span className="tabular-nums">{fmtNumber(b.count)}</span>
                  </li>
                ))}
                <li className="flex justify-between gap-4 text-[color:var(--muted)]">
                  <span>Not provided</span>
                  <span className="tabular-nums">{fmtNumber(ageMissing)}</span>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">
                Gender
              </h3>
              <ul className="mt-3 space-y-1.5 text-sm">
                {[...genderCounts.entries()]
                  .sort((a, b) => b[1] - a[1])
                  .map(([slug, count]) => (
                    <li key={slug} className="flex justify-between gap-4">
                      <span className="capitalize">{slug.replace(/_/g, " ")}</span>
                      <span className="tabular-nums">{fmtNumber(count)}</span>
                    </li>
                  ))}
              </ul>
            </div>
          </div>

          <div>
            <h3 className="small-caps text-xs font-medium text-[color:var(--muted)]">
              Self-reported tradition
            </h3>
            <ul className="mt-3 space-y-1.5 text-sm">
              {[...countBy(runs, (r) => r.tradition_slug ?? "__none__").entries()]
                .sort((a, b) => b[1] - a[1])
                .map(([slug, count]) => (
                  <li key={slug} className="flex justify-between gap-4">
                    <span>
                      {slug === "__none__" ? "Not provided" : (traditionLabel.get(slug) ?? slug)}
                    </span>
                    <span className="tabular-nums">{fmtNumber(count)}</span>
                  </li>
                ))}
            </ul>
          </div>

          <p className="text-xs text-[color:var(--muted)]">
            Data version {QUIZ_DATA.data_version} · {QUIZ_DATA.items.length} statements
          </p>
        </>
      )}
    </section>
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
