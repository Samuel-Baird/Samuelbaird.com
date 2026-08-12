import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { BeehiveMark } from "@/components/beehive-mark";
import { DeseretTitle } from "@/components/deseret-title";
import { Tag } from "@/components/tag";
import { CollapsibleSection } from "@/components/collapsible-section";
import { Quiz } from "@/components/quiz/quiz-section";
import { quizSectionFor } from "@/lib/quiz";

/**
 * A timeline that has been scoped but whose sources have not been gathered
 * yet. It carries the question, the axes the sources will be read against, and
 * its quiz — which matches a reader to a named theological position rather
 * than to a person, since there are no sourced figures to match against yet.
 *
 * When the sources land this page is replaced by the real explorer, and the
 * quiz's figures become the speakers on the timeline.
 */
export function PlannedTimelinePage({
  timeline,
  title,
  deseretTitle,
  question,
  lede,
  axes,
  sourcing,
}: {
  timeline: string;
  title: string;
  /** Plain-string title for the Deseret reveal; must be plain text. */
  deseretTitle: string;
  question: string;
  lede: string;
  /** The axes the sources will be tagged against, once gathered. */
  axes: { title: string; body: string }[];
  /** Where the sources are expected to come from. */
  sourcing: string;
}) {
  const questionCount = quizSectionFor(timeline)?.questions.length ?? 0;

  return (
    <div className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20">
      <Link
        href="/timelines"
        className="inline-flex items-center gap-1.5 text-xs font-medium text-[color:var(--accent)] hover:underline"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        Timelines
      </Link>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <p className="small-caps text-xs font-medium text-[color:var(--accent)]">
          Timeline in preparation
        </p>
        <Tag ink="oxblood">No sources gathered yet</Tag>
      </div>

      <h1 className="serif mt-4 max-w-3xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        <DeseretTitle text={deseretTitle} />
      </h1>
      <p className="mt-5 max-w-3xl text-base leading-relaxed text-[color:var(--muted)]">
        {lede}
      </p>

      <p className="mt-6 max-w-3xl rounded-[var(--radius)] border border-[color:var(--border)] bg-[color:var(--muted-soft)]/60 p-4 text-sm leading-relaxed text-[color:var(--muted)]">
        This page is a placeholder. The question and the axes below are settled; the sources
        are not gathered, so there is nothing here yet to read as evidence. The quiz is
        live, but until the sources land it matches you to a named position rather than to a
        person — no view is attributed to anyone ahead of the research.
      </p>

      <section className="mt-12 lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-start lg:gap-14">
        <div className="min-w-0">
          <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
            The question
          </h2>
          <p className="serif mt-3 max-w-2xl text-xl leading-snug tracking-tight">{question}</p>

          <h2 className="small-caps mt-10 text-xs font-medium text-[color:var(--accent)]">
            Axes the sources will be read against
          </h2>
          <dl className="mt-4 max-w-2xl space-y-4">
            {axes.map((axis) => (
              <div key={axis.title}>
                <dt className="text-sm font-semibold">{axis.title}</dt>
                <dd className="mt-1 text-sm leading-relaxed text-[color:var(--muted)]">
                  {axis.body}
                </dd>
              </div>
            ))}
          </dl>
        </div>

        <aside className="mt-10 lg:mt-0 lg:border-l lg:border-[color:var(--border)] lg:pl-10">
          <h2 className="small-caps text-xs font-medium text-[color:var(--accent)]">
            Where the sources will come from
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-[color:var(--muted)]">{sourcing}</p>
          <p className="mt-4 text-sm leading-relaxed text-[color:var(--muted)]">
            Sources will be graded and typed the same way as on{" "}
            <Link
              href="/eternal-increase-timeline"
              className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
            >
              the eternal-increase timeline
            </Link>
            , which is the finished example of what this becomes.
          </p>
        </aside>
      </section>

      <div className="dinkus" aria-hidden="true">
        <BeehiveMark className="h-4 w-4" />
      </div>

      <CollapsibleSection
        title={`Where do you land on ${title}?`}
        blurb={
          <>
            Answer this timeline&apos;s questions and see which position your answers
            describe. You can also{" "}
            <Link
              href="/quiz"
              className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
            >
              answer every timeline&apos;s questions at once
            </Link>
            .
          </>
        }
        meta={`${questionCount} questions · answers saved to your account`}
        closedLabel="Take the quiz"
        openLabel="Hide the quiz"
      >
        <Quiz timeline={timeline} signInReason="Sign in to take the quiz." />
      </CollapsibleSection>
    </div>
  );
}
