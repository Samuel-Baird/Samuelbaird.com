import { ArrowLeft, ArrowRight } from "lucide-react";
import { displayOptions, responseLabel } from "@/lib/evangelical-quiz";
import type { QuizItem } from "@/lib/evangelical-quiz";
import { GroupBreakdownChart } from "./group-breakdown-chart";

export function QuestionScreen({
  item,
  index,
  total,
  chosen,
  onAnswer,
  onBack,
  onContinue,
  isLast,
}: {
  item: QuizItem;
  /** 0-based position in the question sequence. */
  index: number;
  total: number;
  /** Index into item.scale of the reader's current answer, if any. */
  chosen: number | undefined;
  onAnswer: (responseIndex: number) => void;
  onBack: (() => void) | null;
  onContinue: () => void;
  isLast: boolean;
}) {
  const options = displayOptions(item);
  const progressPct = Math.round((index / total) * 100);
  const answered = chosen !== undefined;

  return (
    <div>
      <div className="flex items-center justify-between gap-4">
        {onBack ? (
          <button
            type="button"
            onClick={onBack}
            className="inline-flex min-h-9 items-center gap-1.5 rounded-[var(--radius)] px-1 text-xs font-medium text-[color:var(--accent)] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
          >
            <ArrowLeft aria-hidden="true" size={13} />
            Back
          </button>
        ) : (
          <span />
        )}
        <p className="small-caps text-[11px] text-[color:var(--muted)]">
          <span className="tabular-nums font-medium text-[color:var(--foreground)]">
            {index + 1}
          </span>{" "}
          of <span className="tabular-nums">{total}</span>
        </p>
      </div>

      <div
        role="progressbar"
        aria-valuenow={index + 1}
        aria-valuemin={1}
        aria-valuemax={total}
        aria-label="Question progress"
        className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-[color:var(--muted-soft)]"
      >
        <div
          className="h-full rounded-full bg-[color:var(--accent)] transition-[width] motion-safe:duration-300"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      <fieldset className="mt-8">
        <legend className="serif text-2xl font-semibold leading-snug tracking-tight sm:text-3xl">
          {item.statement}
        </legend>
        {item.year === 2022 && (
          <p className="mt-2 text-xs text-[color:var(--muted)]">
            <span className="small-caps text-[11px]">2022 wave</span> — this statement was
            dropped from the 2025 survey, but it&apos;s theologically interesting enough
            that we kept it, using the last wave it was asked.
          </p>
        )}
        {item.three_option && (
          <p className="mt-2 text-xs text-[color:var(--muted)]">
            The source only published agree / disagree / not sure for this one, so
            that&apos;s what&apos;s offered here.
          </p>
        )}

        <div className="mt-6 space-y-2.5">
          {options.map(({ response, index: responseIndex }) => {
            const selected = chosen === responseIndex;
            return (
              <button
                key={response}
                type="button"
                onClick={() => onAnswer(responseIndex)}
                aria-pressed={selected}
                className={`block w-full rounded-[var(--radius)] border p-4 text-left text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)] ${
                  selected
                    ? "border-[color:var(--accent)] bg-[color:var(--accent-soft)]"
                    : "border-[color:var(--border)] bg-white hover:bg-[color:var(--muted-soft)]/60"
                }`}
              >
                {responseLabel(response)}
              </button>
            );
          })}
        </div>
      </fieldset>

      {answered && (
        <>
          <button
            type="button"
            onClick={onContinue}
            className="mt-8 inline-flex min-h-11 items-center gap-2 rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
          >
            {isLast ? "See your results" : "Next question"}
            <ArrowRight aria-hidden="true" size={15} />
          </button>

          <GroupBreakdownChart item={item} chosenIndex={chosen} />
        </>
      )}
    </div>
  );
}
