"use client";

import { Check, Loader2, Lock, RotateCcw } from "lucide-react";
import { usePathname } from "next/navigation";
import { useState, useTransition } from "react";
import { clearQuizAnswers, saveQuizAnswer } from "@/app/actions/quiz";
import { useAuthPrompt } from "@/components/auth-prompt";
import { Tag } from "@/components/tag";
import {
  answeredCount,
  optionLabel,
  scoreSection,
  type AnswerMap,
  type QuizSection,
} from "@/lib/quiz";

/**
 * Runs one or more quiz sections. A timeline page passes its own section; the
 * whole-bank quiz passes all of them. Answers save as they are chosen, so the
 * two views are always looking at the same saved answers.
 */
export function QuizRunner({
  sections,
  initialAnswers,
  signedIn,
  /** Copy for the sign-in prompt, in this quiz's terms. */
  signInReason,
}: {
  sections: QuizSection[];
  initialAnswers: AnswerMap;
  signedIn: boolean;
  signInReason: string;
}) {
  const [answers, setAnswers] = useState<AnswerMap>(initialAnswers);
  const [pendingQuestion, setPendingQuestion] = useState<string | null>(null);
  const [failed, setFailed] = useState<string | null>(null);
  const [, startTransition] = useTransition();
  const { requestLogin } = useAuthPrompt();
  const pathname = usePathname() || "/quiz";

  const allQuestions = sections.flatMap((s) => s.questions);
  const answered = answeredCount(allQuestions, answers);

  function choose(questionId: string, optionId: string) {
    if (!signedIn) {
      requestLogin(signInReason);
      return;
    }
    const previous = answers[questionId];
    setAnswers((a) => ({ ...a, [questionId]: optionId }));
    setPendingQuestion(questionId);
    setFailed(null);
    startTransition(async () => {
      try {
        await saveQuizAnswer({ questionId, optionId, currentPath: pathname });
      } catch {
        // Put it back rather than showing a saved answer that is not saved.
        setAnswers((a) => {
          const next = { ...a };
          if (previous) next[questionId] = previous;
          else delete next[questionId];
          return next;
        });
        setFailed("That answer did not save. Check your connection and try again.");
      } finally {
        setPendingQuestion(null);
      }
    });
  }

  function reset(timeline?: string) {
    const scope = timeline
      ? new Set(sections.find((s) => s.timeline === timeline)?.questions.map((q) => q.id))
      : new Set(allQuestions.map((q) => q.id));
    const previous = answers;
    setAnswers((a) => Object.fromEntries(Object.entries(a).filter(([id]) => !scope.has(id))));
    startTransition(async () => {
      try {
        await clearQuizAnswers({ timeline, currentPath: pathname });
      } catch {
        setAnswers(previous);
        setFailed("Those answers could not be cleared.");
      }
    });
  }

  return (
    <div>
      {!signedIn && (
        <div className="mb-6 flex flex-wrap items-center gap-x-4 gap-y-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--accent-soft)] p-4">
          <Lock aria-hidden="true" size={16} className="text-[color:var(--accent)]" />
          <p className="min-w-0 flex-1 text-sm text-[color:var(--foreground)]">
            {signInReason} Your answers are saved to your account, so you can come back to
            them and add the rest later.
          </p>
          <button
            type="button"
            onClick={() => requestLogin(signInReason)}
            className="min-h-10 rounded-[var(--radius)] bg-[color:var(--accent)] px-4 text-sm font-medium text-white"
          >
            Sign in
          </button>
        </div>
      )}

      {failed && (
        <p
          role="status"
          className="mb-4 rounded-[var(--radius)] border border-[color:var(--oxblood)]/40 bg-[color:var(--oxblood-soft)] p-3 text-sm text-[color:var(--oxblood)]"
        >
          {failed}
        </p>
      )}

      {signedIn && (
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-[color:var(--muted)]">
            <span className="tabular-nums font-medium text-[color:var(--foreground)]">
              {answered}
            </span>{" "}
            of <span className="tabular-nums">{allQuestions.length}</span> answered
            {answered > 0 && " · saved to your account"}
          </p>
          {answered > 0 && (
            <button
              type="button"
              onClick={() => reset()}
              className="small-caps inline-flex min-h-9 items-center gap-1.5 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-3 text-xs font-medium hover:bg-[color:var(--muted-soft)]"
            >
              <RotateCcw aria-hidden="true" size={13} />
              Start over
            </button>
          )}
        </div>
      )}

      <div className="space-y-12">
        {sections.map((section) => {
          const sectionAnswered = answeredCount(section.questions, answers);
          const scores = scoreSection(section, answers);
          const top = scores[0];
          const showResult = sectionAnswered > 0 && top && top.comparable > 0;

          return (
            <section key={section.timeline}>
              {sections.length > 1 && (
                <div className="border-b border-[color:var(--border)] pb-3">
                  <h3 className="serif text-xl font-semibold tracking-tight">{section.title}</h3>
                  <p className="mt-1 max-w-2xl text-sm leading-relaxed text-[color:var(--muted)]">
                    {section.blurb}
                  </p>
                </div>
              )}

              <ol className="mt-6 space-y-8">
                {section.questions.map((question, i) => {
                  const chosen = answers[question.id];
                  const saving = pendingQuestion === question.id;
                  return (
                    <li key={question.id}>
                      <fieldset>
                        <legend className="flex items-baseline gap-2 text-base font-medium leading-snug">
                          <span className="small-caps shrink-0 text-xs text-[color:var(--muted)] tabular-nums">
                            {i + 1}
                          </span>
                          <span>{question.prompt}</span>
                          {saving && (
                            <Loader2
                              aria-label="Saving"
                              size={13}
                              className="shrink-0 animate-spin text-[color:var(--muted)] motion-reduce:animate-none"
                            />
                          )}
                        </legend>
                        <div className="mt-3 space-y-2">
                          {question.options.map((option) => {
                            const selected = chosen === option.id;
                            return (
                              <label
                                key={option.id}
                                className={`flex cursor-pointer items-start gap-3 rounded-[var(--radius)] border p-3 transition-colors ${
                                  selected
                                    ? "border-[color:var(--accent)] bg-[color:var(--accent-soft)]"
                                    : "border-[color:var(--border)] bg-white hover:bg-[color:var(--muted-soft)]/60"
                                }`}
                              >
                                <input
                                  type="radio"
                                  name={question.id}
                                  value={option.id}
                                  checked={selected}
                                  onChange={() => choose(question.id, option.id)}
                                  className="mt-1 h-4 w-4 shrink-0 accent-[color:var(--accent)]"
                                />
                                <span className="min-w-0">
                                  <span className="block text-sm leading-relaxed">
                                    {option.label}
                                  </span>
                                  {option.note && (
                                    <span className="mt-0.5 block text-xs leading-relaxed text-[color:var(--muted)]">
                                      {option.note}
                                    </span>
                                  )}
                                </span>
                              </label>
                            );
                          })}
                        </div>
                      </fieldset>
                    </li>
                  );
                })}
              </ol>

              {showResult && (
                <SectionResult
                  section={section}
                  answers={answers}
                  scores={scores}
                  answeredHere={sectionAnswered}
                />
              )}
            </section>
          );
        })}
      </div>
    </div>
  );
}

function SectionResult({
  section,
  answers,
  scores,
  answeredHere,
}: {
  section: QuizSection;
  answers: AnswerMap;
  scores: ReturnType<typeof scoreSection>;
  answeredHere: number;
}) {
  const [top, ...rest] = scores;
  const complete = answeredHere === section.questions.length;
  const questionById = new Map(section.questions.map((q) => [q.id, q]));

  return (
    <div className="mt-8 rounded-[var(--radius)] border border-[color:var(--honey)]/40 bg-[color:var(--honey-soft)]/40 p-5 sm:p-6">
      <p className="small-caps text-[11px] font-medium text-[color:var(--honey)]">
        {complete ? "Your result" : `Result so far — ${answeredHere} of ${section.questions.length} answered`}
      </p>
      <h4 className="serif mt-1 text-2xl font-semibold tracking-tight">
        {top.figure.name}
      </h4>
      {top.figure.qualifier && (
        <p className="serif-onum text-sm text-[color:var(--muted)]">{top.figure.qualifier}</p>
      )}
      <p className="mt-3 max-w-2xl text-sm leading-relaxed">{top.figure.blurb}</p>
      <p className="mt-3 text-sm text-[color:var(--muted)]">
        You agreed on{" "}
        <span className="tabular-nums font-medium text-[color:var(--foreground)]">
          {top.matches}
        </span>{" "}
        of <span className="tabular-nums">{top.comparable}</span>{" "}
        {top.comparable === 1 ? "question" : "questions"} where you both took a position.
      </p>

      {top.disagreements.length > 0 && (
        <div className="mt-4">
          <p className="small-caps text-[10px] font-medium text-[color:var(--muted)]">
            Where you part company
          </p>
          <ul className="mt-1.5 space-y-1 text-sm">
            {top.disagreements.map((qid) => {
              const question = questionById.get(qid);
              if (!question) return null;
              return (
                <li key={qid} className="leading-relaxed">
                  <span className="text-[color:var(--muted)]">{question.short}: </span>
                  you said &ldquo;{optionLabel(question, answers[qid])}&rdquo;
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {rest.length > 0 && (
        <div className="mt-5 border-t border-[color:var(--honey)]/30 pt-4">
          <p className="small-caps text-[10px] font-medium text-[color:var(--muted)]">
            Also close
          </p>
          <ul className="mt-2 flex flex-wrap gap-2">
            {rest
              .filter((s) => s.comparable > 0)
              .slice(0, 4)
              .map((s) => (
                <li key={s.figure.id}>
                  <Tag ink="muted">
                    {s.figure.name} · {Math.round(s.affinity * 100)}%
                  </Tag>
                </li>
              ))}
          </ul>
        </div>
      )}

      {complete && (
        <p className="mt-5 inline-flex items-center gap-1.5 text-xs text-[color:var(--muted)]">
          <Check aria-hidden="true" size={13} />
          Saved to your account
        </p>
      )}
    </div>
  );
}
