import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { ArrowLeft, Trash2 } from "lucide-react";
import { deleteEvangelicalQuizRun } from "@/app/actions/evangelical-quiz";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { getCurrentUser } from "@/lib/auth";
import { TRADITION_LABEL, type Tradition } from "@/lib/evangelical-quiz";
import { fmtDateTime } from "@/lib/format";
import { createSupabaseServiceClient } from "@/lib/supabase/server";

// Unlisted, like the quiz itself.
export const metadata: Metadata = {
  title: "Your quiz results",
  description: "Past results for the How evangelical are you? quiz.",
  robots: { index: false, follow: false },
};

export const dynamic = "force-dynamic";

type RunRow = {
  id: string;
  percentile: number;
  matched_tradition: string | null;
  runner_up_tradition: string | null;
  tie: boolean;
  data_version: string;
  created_at: string;
};

function traditionPhrase(run: RunRow): string {
  const top = run.matched_tradition
    ? (TRADITION_LABEL[run.matched_tradition as Tradition] ?? run.matched_tradition)
    : null;
  const runnerUp = run.runner_up_tradition
    ? (TRADITION_LABEL[run.runner_up_tradition as Tradition] ?? run.runner_up_tradition)
    : null;
  if (!top) return "No tradition match";
  if (run.tie && runnerUp) return `A tie between ${top} and ${runnerUp}`;
  return `Most like ${top}`;
}

export default async function QuizHistoryPage() {
  const auth = await getCurrentUser();
  if (!auth) {
    redirect(`/login?next=${encodeURIComponent("/how-evangelical/history")}`);
  }

  // Runs are deny-all RLS; the service client reads only this user's rows.
  const service = createSupabaseServiceClient();
  const { data } = await service
    .from("evangelical_quiz_runs")
    .select(
      "id, percentile, matched_tradition, runner_up_tradition, tie, data_version, created_at",
    )
    .eq("user_id", auth.user.id)
    .order("created_at", { ascending: false });
  const runs = (data ?? []) as RunRow[];

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href="/how-evangelical"
        className="inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        Back to the quiz
      </Link>

      <h1 className="serif mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="Your quiz results" />
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-relaxed text-[color:var(--muted)]">
        Every time you&apos;ve completed the quiz, newest first. Deleting a result removes
        it permanently — from your history and from the aggregate research data.
      </p>

      {runs.length === 0 ? (
        <p className="mt-10 max-w-xl rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5 text-sm leading-relaxed text-[color:var(--muted)]">
          No completed runs yet.{" "}
          <Link href="/how-evangelical" className="font-medium text-[color:var(--accent)] hover:underline">
            Take the quiz
          </Link>{" "}
          and your result will show up here.
        </p>
      ) : (
        <ul className="mt-10 max-w-2xl space-y-4">
          {runs.map((run) => (
            <li
              key={run.id}
              className="flex flex-wrap items-center justify-between gap-4 rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5"
            >
              <div className="min-w-0">
                <p className="text-sm font-medium">
                  More evangelical than{" "}
                  <span className="tabular-nums">{Math.round(run.percentile)}%</span> of
                  Americans · {traditionPhrase(run)}
                </p>
                <p className="mt-1 text-xs text-[color:var(--muted)]">
                  {fmtDateTime(run.created_at)} · data v{run.data_version}
                </p>
                {Number(run.data_version) < 3 && (
                  <p className="mt-1 text-xs text-[color:var(--muted)]">
                    This percentile used a simulated reference population, since replaced
                    with real survey respondents.
                  </p>
                )}
              </div>
              <form
                action={async () => {
                  "use server";
                  await deleteEvangelicalQuizRun({
                    runId: run.id,
                    currentPath: "/how-evangelical/history",
                  });
                }}
              >
                <button
                  type="submit"
                  className="inline-flex min-h-9 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] px-3 text-xs font-medium text-[color:var(--oxblood)] hover:bg-[color:var(--oxblood-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
                >
                  <Trash2 aria-hidden="true" size={13} />
                  Delete
                </button>
              </form>
            </li>
          ))}
        </ul>
      )}

      <div className="dinkus mt-14" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
