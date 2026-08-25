import { QUIZ_DATA, QUIZ_IS_COMPLETE, QUIZ_QUESTION_COUNT } from "@/lib/evangelical-quiz";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { HowItWorks } from "./how-it-works";

export function LandingScreen({ onStart }: { onStart: () => void }) {
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

      <button
        type="button"
        onClick={onStart}
        className="mt-8 inline-flex min-h-11 items-center rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
      >
        Start
      </button>

      <div className="mt-12">
        <HowItWorks />
      </div>

      <div className="dinkus mt-10" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>
    </div>
  );
}
