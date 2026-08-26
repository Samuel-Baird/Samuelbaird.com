"use client";

import Link from "next/link";
import { ArrowLeft, History, RotateCcw } from "lucide-react";
import { useAuthPrompt } from "@/components/auth-prompt";
import { BeehiveMark } from "@/components/beehive-mark";
import {
  breakdown,
  matchTradition,
  percentileOf,
  QUIZ_DATA,
  scoreAnswers,
  TRADITION_LABEL,
  type AnswerMap,
  type BreakdownRow,
} from "@/lib/evangelical-quiz";
import { HowItWorks } from "./how-it-works";
import { ShareButton } from "./share-button";

const ANSWER_VERB: Record<string, string> = {
  strongly_agree: "strongly agreed",
  somewhat_agree: "somewhat agreed",
  somewhat_disagree: "somewhat disagreed",
  strongly_disagree: "strongly disagreed",
  not_sure: "weren't sure",
};

function directionPhrase(row: BreakdownRow): string {
  const magnitude = Math.abs(row.contribution).toFixed(2);
  return row.contribution >= 0
    ? `That made you ${magnitude} more evangelical.`
    : `That made you ${magnitude} less evangelical.`;
}

export function ResultsScreen({
  answers,
  onRetake,
  datasetHref,
  signedIn,
}: {
  answers: AnswerMap;
  onRetake: () => void;
  /** Where the top-of-page "back" link should go, once the quiz is done. */
  datasetHref: string | null;
  signedIn: boolean;
}) {
  const score = scoreAnswers(QUIZ_DATA, answers);
  const percentile = percentileOf(QUIZ_DATA, score);
  const match = matchTradition(QUIZ_DATA, answers);
  const rows = breakdown(QUIZ_DATA, answers);
  const { requestLogin } = useAuthPrompt();

  const shareText = buildShareText(percentile, match);

  return (
    <div>
      {datasetHref && (
        <Link
          href={datasetHref}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
        >
          <ArrowLeft aria-hidden="true" size={13} />
          Back to Data Explorer
        </Link>
      )}

      <p className="small-caps mt-6 text-[11px] font-medium text-[color:var(--honey)]">
        Your result
      </p>

      {match && (
        <h1 className="serif mt-1 text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">
          {match.tie ? (
            <>
              You answer about as much like{" "}
              {TRADITION_LABEL[match.top.tradition]} as{" "}
              {TRADITION_LABEL[match.runnerUp.tradition]}.
            </>
          ) : (
            <>You answer most like {TRADITION_LABEL[match.top.tradition]}.</>
          )}
        </h1>
      )}
      {match && !match.tie && (
        <p className="mt-2 text-sm text-[color:var(--muted)]">
          Runner-up: {TRADITION_LABEL[match.runnerUp.tradition]}.
        </p>
      )}
      {match && (
        <p className="mt-3 max-w-xl text-xs leading-relaxed text-[color:var(--muted)]">
          Subgroup sample sizes are small — when the top two traditions are this close,
          the honest read is a tie, not a confident winner.
        </p>
      )}

      <div className="mt-6 rounded-[var(--radius)] border border-[color:var(--accent)]/40 bg-[color:var(--accent-soft)] p-5 sm:p-6">
        <p className="small-caps text-[11px] font-medium text-[color:var(--accent)]">
          Evangelical percentile
        </p>
        <p className="serif mt-1 text-2xl font-semibold tracking-tight sm:text-3xl">
          You answered more like an evangelical than{" "}
          <span className="tabular-nums">{Math.round(percentile)}%</span> of Americans.
        </p>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <ShareButton text={shareText} />
        {signedIn && (
          <Link
            href="/how-evangelical/history"
            className="inline-flex min-h-10 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm font-medium hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
          >
            <History aria-hidden="true" size={15} />
            Past results
          </Link>
        )}
      </div>

      {/* The spec's "save this result" moment: a skippable sign-in nudge at
          the point of highest motivation. The run is already recorded
          anonymously; signing in here claims it (and any earlier ones) into
          the account via the existing claim-on-sign-in effect. */}
      {!signedIn && (
        <div className="mt-6 flex flex-wrap items-center gap-x-4 gap-y-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)]/60 p-4">
          <p className="min-w-0 flex-1 text-sm leading-relaxed text-[color:var(--muted)]">
            Want to keep this result? Sign in and it&apos;s saved to your account — along
            with any future retakes.
          </p>
          <button
            type="button"
            onClick={() => requestLogin("Sign in to save this result to your account.")}
            className="min-h-10 rounded-[var(--radius)] bg-[color:var(--accent)] px-4 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
          >
            Save this result
          </button>
        </div>
      )}

      <section className="mt-12">
        <h2 className="serif text-xl font-semibold tracking-tight sm:text-2xl">
          The breakdown
        </h2>
        <p className="mt-1.5 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
          Every question you answered, ranked by how much it moved your score — and in
          which direction. A statement pushing you the &ldquo;wrong&rdquo; way usually
          means evangelicals as a group answer it differently than you might expect.
        </p>

        <ol className="mt-6 space-y-3">
          {rows.map((row) => {
            const positive = row.contribution >= 0;
            return (
              <li
                key={row.item.id}
                className={`rounded-[var(--radius)] border-l-4 border border-[color:var(--border)] bg-white p-4 ${
                  positive ? "border-l-[color:var(--accent)]" : "border-l-[color:var(--oxblood)]"
                }`}
              >
                <p className="text-sm leading-relaxed">
                  &ldquo;{row.item.statement}&rdquo; — you {ANSWER_VERB[row.response]}.
                </p>
                <p
                  className={`mt-1.5 text-sm font-medium tabular-nums ${
                    positive ? "text-[color:var(--accent)]" : "text-[color:var(--oxblood)]"
                  }`}
                >
                  {directionPhrase(row)}
                </p>
                {row.item.year === 2022 && (
                  <p className="small-caps mt-1.5 text-[10px] text-[color:var(--muted)]">
                    2022 wave — dropped from the 2025 survey; kept here as
                    theologically interesting
                  </p>
                )}
              </li>
            );
          })}
        </ol>
      </section>

      <div className="mt-12">
        <HowItWorks />
      </div>

      <div className="mt-8">
        <button
          type="button"
          onClick={onRetake}
          className="small-caps inline-flex min-h-10 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-xs font-medium hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
        >
          <RotateCcw aria-hidden="true" size={13} />
          Start over
        </button>
      </div>

      <div className="dinkus mt-10" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}

function buildShareText(
  percentile: number,
  match: ReturnType<typeof matchTradition>,
): string {
  const lines = [
    `I answered more like an evangelical than ${Math.round(percentile)}% of Americans.`,
  ];
  if (match) {
    lines.push(
      match.tie
        ? `I'm about as close to ${match.top.tradition} as ${match.runnerUp.tradition}.`
        : `I answer most like ${match.top.tradition} (runner-up: ${match.runnerUp.tradition}).`,
    );
  }
  lines.push("Take the quiz: https://latter-day-stats.vercel.app/how-evangelical");
  return lines.join("\n");
}
