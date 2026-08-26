import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Tag } from "@/components/tag";
import { DemographicsEditor } from "@/components/evangelical-quiz/demographics-editor";
import { requireUser } from "@/lib/auth";
import { getQuizAnswersForUser } from "@/lib/quiz/answers";
import { demographicsFromRow } from "@/lib/evangelical-quiz/demographics-row";
import { QUIZ_SECTIONS, answeredCount, optionLabel, scoreSection } from "@/lib/quiz";

export const metadata: Metadata = {
  title: "Quiz results",
  robots: { index: false, follow: false },
};

export const dynamic = "force-dynamic";

export default async function MeQuizPage() {
  const { user, profile } = await requireUser();
  const answers = await getQuizAnswersForUser(user.id);
  const total = QUIZ_SECTIONS.reduce((n, s) => n + s.questions.length, 0);
  const answeredAll = QUIZ_SECTIONS.reduce(
    (n, s) => n + answeredCount(s.questions, answers),
    0,
  );

  return (
    <div className="mt-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="serif text-2xl font-semibold tracking-tight">Quiz results</h1>
          <p className="mt-1 text-sm text-[color:var(--muted)]">
            <span className="tabular-nums">{answeredAll}</span> of{" "}
            <span className="tabular-nums">{total}</span> questions answered across{" "}
            <span className="tabular-nums">{QUIZ_SECTIONS.length}</span> timelines.
          </p>
        </div>
        <Link
          href="/quiz"
          className="inline-flex min-h-10 items-center gap-2 rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm font-medium hover:bg-[color:var(--muted-soft)]"
        >
          {answeredAll === 0 ? "Take the quiz" : "Change your answers"}
          <ArrowRight aria-hidden="true" size={14} />
        </Link>
      </div>

      {answeredAll === 0 ? (
        <div className="mt-6 rounded-[var(--radius)] border border-dashed border-[color:var(--border)] bg-white p-8 text-center text-sm text-[color:var(--muted)]">
          You have not answered any questions yet. The quiz asks what each timeline asks of
          its sources, and tells you which figures you come out closest to.
        </div>
      ) : (
        <div className="mt-6 grid gap-5 lg:grid-cols-2">
          {QUIZ_SECTIONS.map((section) => {
            const done = answeredCount(section.questions, answers);
            const [top] = scoreSection(section, answers);
            const matched = done > 0 && top && top.comparable > 0;
            return (
              <section
                key={section.timeline}
                className="rounded-[var(--radius)] border border-[color:var(--border)] bg-white p-5"
              >
                <div className="flex items-start justify-between gap-3">
                  <h2 className="serif text-lg font-semibold leading-snug tracking-tight">
                    <Link href={section.timeline} className="hover:text-[color:var(--accent)]">
                      {section.title}
                    </Link>
                  </h2>
                  <Tag ink={done === section.questions.length ? "accent" : "muted"}>
                    {done}/{section.questions.length}
                  </Tag>
                </div>

                {matched ? (
                  <>
                    <p className="small-caps mt-4 text-[10px] font-medium text-[color:var(--muted)]">
                      Closest to
                    </p>
                    <p className="serif text-xl font-semibold tracking-tight">
                      {top.figure.name}
                    </p>
                    <p className="mt-1 text-xs text-[color:var(--muted)]">
                      Agreed on <span className="tabular-nums">{top.matches}</span> of{" "}
                      <span className="tabular-nums">{top.comparable}</span> comparable{" "}
                      {top.comparable === 1 ? "question" : "questions"}
                    </p>
                    <ul className="mt-4 space-y-1.5 border-t border-[color:var(--border)] pt-3">
                      {section.questions.map((q) => {
                        const label = optionLabel(q, answers[q.id]);
                        return (
                          <li key={q.id} className="text-xs leading-relaxed">
                            <span className="text-[color:var(--muted)]">{q.short}: </span>
                            {label ?? (
                              <span className="italic text-[color:var(--muted)]">
                                not answered
                              </span>
                            )}
                          </li>
                        );
                      })}
                    </ul>
                  </>
                ) : (
                  <p className="mt-4 text-sm text-[color:var(--muted)]">
                    Not started.{" "}
                    <Link
                      href={section.timeline}
                      className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
                    >
                      Answer this timeline&apos;s questions
                    </Link>
                    .
                  </p>
                )}
              </section>
            );
          })}
        </div>
      )}

      <DemographicsEditor initial={demographicsFromRow(profile)} />
    </div>
  );
}
