import Link from "next/link";
import { QUIZ_DATA, QUIZ_IS_COMPLETE, QUIZ_QUESTION_COUNT } from "@/lib/evangelical-quiz";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { HowItWorks } from "./how-it-works";

export function LandingScreen({
  answeredCount,
  hasFinished,
  signedIn,
  onStart,
  onResume,
  onViewResults,
}: {
  /** How many of this reader's answers are already saved (0 unless signed in). */
  answeredCount: number;
  /** True once every current item has a saved answer. */
  hasFinished: boolean;
  signedIn: boolean;
  onStart: () => void;
  onResume: () => void;
  onViewResults: () => void;
}) {
  const inProgress = answeredCount > 0 && !hasFinished;

  return (
    <div>
      <h1 className="serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text="How evangelical are you?" />
      </h1>
      <p className="mt-5 max-w-xl text-base leading-relaxed text-[color:var(--muted)]">
        Answer{" "}
        <span className="tabular-nums font-medium text-[color:var(--foreground)]">
          {QUIZ_QUESTION_COUNT}
        </span>{" "}
        belief statements from a national survey, and see which religious tradition
        your answers land closest to — and how evangelical your answers are compared
        to the rest of the country.
      </p>

      {!QUIZ_IS_COMPLETE && (
        <p className="mt-4 max-w-xl rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)]/60 p-3 text-xs leading-relaxed text-[color:var(--muted)]">
          This instrument has {QUIZ_DATA.expected_items} statements in total; only{" "}
          {QUIZ_QUESTION_COUNT} currently have survey data loaded, so that&apos;s what
          you&apos;ll be asked today. The rest will appear once their numbers are entered.
        </p>
      )}

      <div className="mt-8 flex flex-wrap items-center gap-3">
        {hasFinished ? (
          <>
            <button
              type="button"
              onClick={onViewResults}
              className="inline-flex min-h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
            >
              View results
            </button>
            <button
              type="button"
              onClick={onStart}
              className="inline-flex min-h-11 items-center rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-6 text-sm font-medium hover:bg-[color:var(--muted-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
            >
              Retake
            </button>
          </>
        ) : inProgress ? (
          <button
            type="button"
            onClick={onResume}
            className="inline-flex min-h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
          >
            Continue ({answeredCount} of {QUIZ_QUESTION_COUNT} answered)
          </button>
        ) : (
          <button
            type="button"
            onClick={onStart}
            className="inline-flex min-h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
          >
            Start
          </button>
        )}
        {signedIn && (
          <Link
            href="/how-evangelical/history"
            className="text-sm font-medium text-[color:var(--accent)] hover:underline"
          >
            Past results
          </Link>
        )}
      </div>

      <div className="mt-12">
        <HowItWorks />
      </div>

      <div className="dinkus mt-10" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
